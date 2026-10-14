import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// Each tab is its own docs instance; markdown is read in place from the source folders.
const defaultExclude = [
  '**/_*.{js,jsx,ts,tsx,md,mdx}',
  '**/_*/**',
  '**/*.test.{js,jsx,ts,tsx}',
  '**/__tests__/**',
];

const tabs = [
  {id: 'default', route: 'datastructures', path: 'docs-ds', label: 'Data Structures'},
  {id: 'interview-prep', route: 'interview-prep', path: '../interview_prep', label: 'Interview Preparation'},
  {id: 'pde', route: 'pde', path: '../pde_certification', label: 'PDE Certification'},
  {id: 'notes', route: 'notes', path: '../notes', label: 'My Notes'},
];

const config: Config = {
  title: 'Data Engineering Roadmap',
  tagline: 'Data structures, interview prep, GCP PDE certification and notes',
  favicon: 'img/favicon.ico',

  future: {v4: true},

  url: 'https://learnhowtocode12.github.io',
  baseUrl: '/dataengineering/',
  organizationName: 'learnhowtocode12',
  projectName: 'dataengineering',

  onBrokenLinks: 'throw',

  // Source markdown is plain CommonMark (contains <details>, raw < and { characters).
  markdown: {
    format: 'detect',
    hooks: {onBrokenMarkdownLinks: 'warn'},
  },

  i18n: {defaultLocale: 'en', locales: ['en']},

  presets: [
    [
      'classic',
      {
        docs: false,
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      } satisfies Preset.Options,
    ],
  ],

  plugins: tabs.map(
    (t) =>
      [
        '@docusaurus/plugin-content-docs',
        {
          id: t.id,
          path: t.path,
          routeBasePath: t.route,
          // creds.md must never be published.
          exclude: [...defaultExclude, '**/creds.md'],
        },
      ] as [string, object],
  ),

  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexBlog: false,
        docsRouteBasePath: tabs.map((t) => t.route),
        docsDir: tabs.map((t) => t.path),
      },
    ],
  ],

  themeConfig: {
    colorMode: {respectPrefersColorScheme: true},
    navbar: {
      title: 'Data Engineering Roadmap',
      items: tabs.map((t) => ({
        type: 'docSidebar' as const,
        docsPluginId: t.id,
        sidebarId: 'defaultSidebar',
        position: 'left' as const,
        label: t.label,
      })),
    },
    footer: {
      style: 'dark',
      copyright: 'Data Engineering Roadmap',
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['sql', 'bash', 'yaml', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
