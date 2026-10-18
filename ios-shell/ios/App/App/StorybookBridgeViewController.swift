import AVFoundation
import Capacitor
import UIKit
import WebKit

#if DEBUG
/// Debug builds write the boot trace to Documents/boot.log. The unified log is
/// not reliable enough to answer "did the shim actually install?" from the
/// command line, and a native layer that silently never loads looks exactly like
/// a working one.
func bootLog(_ line: String) {
    guard let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else { return }
    let url = dir.appendingPathComponent("boot.log")
    let entry = "\(Date()): \(line)\n"
    guard let data = entry.data(using: .utf8) else { return }
    if let handle = try? FileHandle(forWritingTo: url) {
        handle.seekToEndOfFile()
        handle.write(data)
        try? handle.close()
    } else {
        try? data.write(to: url)
    }
}
#endif

/// The native half of the Free Baby Stories shell.
///
/// The app is the live storybook at toddler-stories.robbie.digital, wrapped.
/// The four things a live origin cannot do for itself on iOS live here:
///
/// 1. **The screen stays awake while a story is open.** A parent reading aloud
///    is not touching the screen, which is exactly the situation the idle timer
///    is designed to punish: five minutes into a tale the display dims and the
///    child loses the picture. The shim reports when a `#story/<id>` route is
///    open; the timer is released the moment the reader goes back to the shelf.
///
/// 2. **Status bar that follows the paper.** A WKWebView never propagates the
///    page's own background to UIKit, so on a dark system appearance the status
///    bar can end up invisible against the cream. The shim reports the resolved
///    background and this class samples its luminance.
///
/// 3. **Touch behaviour that does not feel like a web page.** No grey tap
///    flash on the illustrations, no double-tap zoom delay, no rubber-band
///    overscroll pulling the page off its own masthead, and a light haptic on
///    the controls the reader actually presses.
///
/// 4. **The voice that reads the story.** A night's reading should not need
///    the phone held open and lit. Long-pressing a story plate asks iOS to read
///    the visible story text aloud with `AVSpeechSynthesizer` — which a web
///    view cannot reach, because iOS Safari exposes no speech synthesis to a
///    page — so the parent can put the phone face-down and still hear the tale.
///
/// This deliberately does not touch Capacitor's navigation delegate: that
/// delegate is what keeps the storybook's own origin inside the web view.
final class StorybookBridgeViewController: CAPBridgeViewController {

    private static let handlerName = "storybookNative"

    private var isDarkBackground = false
    private let speaker = AVSpeechSynthesizer()
    private var isSpeaking = false

    // MARK: - Web view setup

    /// Capacitor rebuilds the web view's userContentController as the bridge
    /// comes up, so it is installed from both hooks — which one runs last is not
    /// part of Capacitor's public contract, and an app whose shim silently never
    /// loads is an app with no native layer at all.
    ///
    /// Installing twice is free: the shim returns immediately if it is already
    /// present. The handler is removed first so a message can never be delivered
    /// twice.
    private func installShim() {
        guard let controller = webView?.configuration.userContentController else {
            bootLog("installShim: no userContentController yet")
            return
        }
        controller.removeScriptMessageHandler(forName: Self.handlerName)
        controller.add(self, name: Self.handlerName)
        controller.addUserScript(
            WKUserScript(
                source: Self.shim,
                injectionTime: .atDocumentStart,
                forMainFrameOnly: true
            )
        )
        bootLog("installShim: shim installed on \(Unmanaged.passUnretained(controller).toOpaque())")
    }

    override func capacitorDidLoad() {
        bootLog("capacitorDidLoad")
        installShim()
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        bootLog("viewDidLoad webView=\(webView == nil ? "nil" : "ready")")
        installShim()
        guard let webView = webView else { return }
        // The storybook owns its safe-area spacing, so the scroll view must not
        // inset the content as well. This mirrors ios.contentInset in
        // capacitor.config.ts — the two have to agree.
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.keyboardDismissMode = .interactive
        webView.allowsBackForwardNavigationGestures = true
        checkForOfflineStart()
    }

    override var preferredStatusBarStyle: UIStatusBarStyle {
        isDarkBackground ? .lightContent : .darkContent
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        pushSafeAreaInsets()
    }

    /// UIKit is the only side that knows the real insets. The storybook is built
    /// for browser chrome that supplies them and does not declare
    /// `viewport-fit=cover`, so `env(safe-area-inset-*)` resolves to 0 inside
    /// the web view and its sticky masthead would sit under the status bar. The
    /// insets are measured here and posted to the page, which applies them to
    /// its own sticky chrome.
    override func viewSafeAreaInsetsDidChange() {
        super.viewSafeAreaInsetsDidChange()
        pushSafeAreaInsets()
    }

    private func pushSafeAreaInsets() {
        guard let webView = webView else { return }
        let insets = view.safeAreaInsets
        webView.evaluateJavaScript(
            "window.__storybookInsets && window.__storybookInsets("
                + "\(Int(insets.top.rounded())), \(Int(insets.bottom.rounded())), "
                + "\(Int(insets.left.rounded())), \(Int(insets.right.rounded())))",
            completionHandler: nil
        )
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        stopSpeaking()
        UIApplication.shared.isIdleTimerDisabled = false
    }

    // MARK: - Offline start

    /// The shell loads a live origin, so a cold start with no connection would
    /// otherwise leave a blank screen. If the shim is not present a few seconds
    /// in, the page never loaded, and the offline fallback says so.
    private func checkForOfflineStart() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 8) { [weak self] in
            guard let self = self, let webView = self.webView else { return }
            webView.evaluateJavaScript("!!window.__storybookNative") { result, _ in
                guard (result as? Bool) != true else { return }
                self.showOfflineNotice()
            }
        }
    }

    private func showOfflineNotice() {
        guard let webView = webView, webView.viewWithTag(0x5F0) == nil else { return }
        let notice = UILabel()
        notice.tag = 0x5F0
        notice.text = "The stories can't be reached.\nCheck your connection, then reopen the app."
        notice.numberOfLines = 0
        notice.textAlignment = .center
        notice.textColor = .secondaryLabel
        notice.font = .preferredFont(forTextStyle: .callout)
        notice.translatesAutoresizingMaskIntoConstraints = false
        webView.addSubview(notice)
        NSLayoutConstraint.activate([
            notice.centerXAnchor.constraint(equalTo: webView.centerXAnchor),
            notice.centerYAnchor.constraint(equalTo: webView.centerYAnchor),
            notice.widthAnchor.constraint(equalToConstant: 260),
        ])
    }

    // MARK: - Reading

    private func setReading(_ reading: Bool) {
        UIApplication.shared.isIdleTimerDisabled = reading
    }

    private func applyBackground(_ dark: Bool) {
        guard dark != isDarkBackground else { return }
        isDarkBackground = dark
        setNeedsStatusBarAppearanceUpdate()
    }

    private func haptic(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.prepare()
        generator.impactOccurred()
    }

    // MARK: - Read aloud

    /// Reads the text the reader is looking at. The web view has no speech
    /// synthesis of its own on iOS, so the words come across as one string and
    /// iOS speaks them.
    private func speak(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            presentNotice("There is nothing on this page to read aloud yet.")
            return
        }
        stopSpeaking()
        do {
            // Spoken audio, not an alarm: the session must not interrupt music
            // permanently and must still be heard with the ringer switch off.
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            // A failed session still speaks; it is just quieter than intended.
        }
        let utterance = AVSpeechUtterance(string: trimmed)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-GB") ?? AVSpeechSynthesisVoice(language: "en-US")
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate * 0.86
        utterance.pitchMultiplier = 1.02
        utterance.postUtteranceDelay = 0.28
        isSpeaking = true
        speaker.delegate = self
        speaker.speak(utterance)
        postToPage("speaking:start")
    }

    private func stopSpeaking() {
        guard isSpeaking else { return }
        isSpeaking = false
        speaker.stopSpeaking(at: .immediate)
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
        postToPage("speaking:stop")
    }

    /// Lets the page show that it is being read aloud (and stop if asked).
    private func postToPage(_ event: String) {
        guard let webView = webView else { return }
        webView.evaluateJavaScript("window.__storybookVoice && window.__storybookVoice('\(event)')", completionHandler: nil)
    }

    private func presentNotice(_ text: String) {
        let alert = UIAlertController(title: "Read aloud", message: text, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    // MARK: - Shim

    /// Injected before any page script runs, on the live origin.
    private static let shim = """
    (function () {
      if (window.__storybookNative) { return; }
      var handler = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.storybookNative;
      if (!handler) { return; }
      function post(message) { try { handler.postMessage(message); } catch (error) {} }
      window.__storybookNative = { post: post };

      // A story route is #story/<id>, a song is #song/<id>; the shelf is
      // everything else. Both are pages a parent reads aloud.
      var reading = false;
      function reportRoute() {
        var isReading = /^#\\/?(story|tale|song)\\//.test(location.hash);
        if (isReading === reading) { return; }
        reading = isReading;
        post(isReading ? 'reader:on' : 'reader:off');
      }

      function relativeLuminance(colour) {
        var parts = /rgba?\\((\\d+)[,\\s]+(\\d+)[,\\s]+(\\d+)/.exec(colour || '');
        if (!parts) { return null; }
        return (0.2126 * +parts[1] + 0.7152 * +parts[2] + 0.0722 * +parts[3]) / 255;
      }

      var _probe = null;
      // Safari keeps oklch() in a computed colour, so the string is not always
      // parseable directly. Canvas resolves any CSS colour to rgb; an
      // unparseable value leaves the sentinel behind.
      function rgbOf(colour) {
        if (!colour) { return null; }
        if (/^rgba?\\(/i.test(colour)) { return colour; }
        if (!_probe) {
          var canvas = document.createElement('canvas');
          canvas.width = 1;
          canvas.height = 1;
          _probe = canvas.getContext('2d');
        }
        _probe.fillStyle = '#010203';
        _probe.fillStyle = colour;
        return _probe.fillStyle === '#010203' ? null : _probe.fillStyle;
      }

      function reportAppearance() {
        var root = getComputedStyle(document.documentElement).backgroundColor;
        if (!root || root === 'rgba(0, 0, 0, 0)' || root === 'transparent') {
          root = getComputedStyle(document.body).backgroundColor;
        }
        var luminance = relativeLuminance(rgbOf(root));
        if (luminance === null) { return; }
        post(luminance < 0.5 ? 'appearance:dark' : 'appearance:light');
      }

      var TAP = 'button, [role="button"], a, .card, .plate, input[type="submit"]';

      function installTouchBehaviour() {
        var style = document.createElement('style');
        style.setAttribute('data-storybook-native', '');
        style.textContent = [
          'html{-webkit-tap-highlight-color:transparent;overscroll-behavior:none}',
          'body{touch-action:manipulation}',
          TAP + '{-webkit-user-select:none;user-select:none}'
        ].join('');
        (document.head || document.documentElement).appendChild(style);
      }

      // The storybook declares no viewport-fit, so env(safe-area-inset-*) is 0
      // in the web view and the sticky masthead would sit under the status bar.
      // The real insets come from UIKit; they land on :root and are applied to
      // the storybook's own chrome here. !important so nothing in the site's
      // stylesheet can win the tie.
      function installSafeArea() {
        var style = document.createElement('style');
        style.setAttribute('data-storybook-native-safe-area', '');
        style.textContent = [
          ':root{--app-safe-top:0px;--app-safe-bottom:0px;--app-safe-left:0px;--app-safe-right:0px}',
          '.masthead{padding-top:var(--app-safe-top) !important}',
          'body{padding-bottom:var(--app-safe-bottom) !important;',
          'padding-left:var(--app-safe-left) !important;',
          'padding-right:var(--app-safe-right) !important}',
          // the back-to-top button is fixed to the viewport, so the body
          // padding cannot reach it
          '.to-top{bottom:calc(var(--app-safe-bottom) + clamp(1rem, 3vw, 2rem)) !important}'
        ].join('');
        (document.head || document.documentElement).appendChild(style);
      }

      window.__storybookInsets = function (top, bottom, left, right) {
        var root = document.documentElement.style;
        root.setProperty('--app-safe-top', top + 'px');
        root.setProperty('--app-safe-bottom', bottom + 'px');
        root.setProperty('--app-safe-left', left + 'px');
        root.setProperty('--app-safe-right', right + 'px');
      };

      // Long-press a story plate to hand its text to iOS to read aloud.
      var LONG_PRESS_MS = 500;
      var pressTimer = null;
      var longPressed = false;

      function storyText() {
        var scope = document.querySelector('article, .story, .tale, main') || document.body;
        var paragraphs = scope.querySelectorAll('p');
        var chunks = [];
        for (var i = 0; i < paragraphs.length; i++) {
          var text = (paragraphs[i].textContent || '').trim();
          if (text) { chunks.push(text); }
        }
        return chunks.join('\\n\\n').slice(0, 4000);
      }

      document.addEventListener('pointerdown', function (event) {
        var target = event.target;
        if (!target || !target.closest) { return; }
        var control = target.closest(TAP);
        if (control && !control.disabled) { post('haptic:light'); }
        longPressed = false;
        clearTimeout(pressTimer);
        if (reading) {
          pressTimer = setTimeout(function () {
            longPressed = true;
            post({ cmd: 'speak', text: storyText() });
          }, LONG_PRESS_MS);
        }
      }, true);

      ['pointerup', 'pointercancel', 'pointermove', 'scroll'].forEach(function (name) {
        document.addEventListener(name, function () { clearTimeout(pressTimer); }, true);
      });

      // A long press must not also open the story.
      document.addEventListener('click', function (event) {
        if (!longPressed) { return; }
        longPressed = false;
        event.preventDefault();
        event.stopImmediatePropagation();
      }, true);

      // The page may hide its own chrome while iOS is speaking.
      window.__storybookVoice = function () {};

      // Hold Capacitor's splash until the page has painted something. A live
      // origin is far slower to first paint than a bundled bundle, and the
      // splash is the app's own mark on the same paper, so holding it beats a
      // blank page. launchShowDuration in capacitor.config.ts is the backstop.
      function hideSplashWhenPainted() {
        var deadline = Date.now() + 9000;
        function painted() {
          return document.readyState === 'complete'
            && !!document.querySelector('h1, main, article, .card');
        }
        function hide() {
          var plugins = window.Capacitor && window.Capacitor.Plugins;
          if (!plugins || !plugins.SplashScreen) { return; }
          try { plugins.SplashScreen.hide(); } catch (error) {}
        }
        (function poll() {
          if (painted() || Date.now() > deadline) {
            // two frames, so what "complete" describes is actually on screen
            requestAnimationFrame(function () { requestAnimationFrame(hide); });
            return;
          }
          setTimeout(poll, 150);
        })();
      }

      function start() {
        installTouchBehaviour();
        installSafeArea();
        reportAppearance();
        reportRoute();
        post('insets:request');
        hideSplashWhenPainted();
        var observer = new MutationObserver(reportAppearance);
        var filter = ['class', 'style', 'data-theme'];
        observer.observe(document.documentElement, { attributes: true, attributeFilter: filter });
        if (document.body) {
          observer.observe(document.body, { attributes: true, attributeFilter: filter });
        }
        window.addEventListener('hashchange', reportRoute);
        window.addEventListener('popstate', reportRoute);
        setInterval(reportRoute, 400);
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start, { once: true });
      } else {
        start();
      }
    })();
    """
}

// MARK: - Messages from the shim

extension StorybookBridgeViewController: WKScriptMessageHandler {

    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        guard message.name == Self.handlerName else { return }
        bootLog("native message: \(String(describing: message.body))")
        if let command = message.body as? String {
            switch command {
            case "appearance:dark":
                applyBackground(true)
            case "appearance:light":
                applyBackground(false)
            case "reader:on":
                setReading(true)
            case "reader:off":
                setReading(false)
                stopSpeaking()
            case "haptic:light":
                haptic(.light)
            case "insets:request":
                pushSafeAreaInsets()
            default:
                break
            }
            return
        }
        if let payload = message.body as? [String: Any], payload["cmd"] as? String == "speak" {
            speak(payload["text"] as? String ?? "")
        }
    }
}

// MARK: - Speech

extension StorybookBridgeViewController: AVSpeechSynthesizerDelegate {

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        finishSpeaking()
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        finishSpeaking()
    }

    private func finishSpeaking() {
        guard isSpeaking else { return }
        isSpeaking = false
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
        postToPage("speaking:stop")
    }
}
