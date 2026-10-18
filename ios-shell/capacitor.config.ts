import type { CapacitorConfig } from '@capacitor/cli';

/**
 * Free Baby Stories — iOS shell.
 *
 * The storybook is a single self-contained HTML file served from
 * toddler-stories.robbie.digital. It is fully static, so the shell simply
 * loads the live origin; the copy in `public/` is the offline fallback for
 * the first launch frame and for a cold start with no signal.
 *
 * backgroundColor #FBF4E6 is the storybook's <meta name="theme-color"> and
 * the cream of its paper, so the launch screen and the page's own background
 * are the same colour and the transition is invisible.
 *
 * contentInset 'never' keeps the storybook's own fixed bars in charge of the
 * safe-area insets (see capacitor.config.ts in the Sprout shell for the long
 * version of why 'always' is wrong here).
 */
const config: CapacitorConfig = {
  appId: 'digital.robbie.babystories',
  appName: 'Free Baby Stories',
  webDir: 'public',
  server: {
    url: 'https://toddler-stories.robbie.digital',
    allowNavigation: ['toddler-stories.robbie.digital'],
    cleartext: false,
  },
  ios: {
    backgroundColor: '#FBF4E6',
    contentInset: 'never',
  },
  plugins: {
    SplashScreen: {
      backgroundColor: '#FBF4E6',
      // The splash is the app's own mark on the same paper, and a live origin
      // paints far later than a bundled bundle does. The shim hides it as soon
      // as the page has actually painted; this is the backstop for a page that
      // never does.
      launchAutoHide: true,
      launchShowDuration: 12000,
      showSpinner: false,
    },
  },
};

export default config;
