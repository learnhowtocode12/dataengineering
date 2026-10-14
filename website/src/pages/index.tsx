import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

import styles from './index.module.css';

const learningPaths = [
  {
    to: '/datastructures/',
    step: '01 / Build foundations',
    title: 'Data Structures',
    text: 'Learn the building blocks behind efficient, reliable data systems, with Big-O notes and runnable Python.',
    linkText: 'Explore 16 concepts',
  },
  {
    to: '/interview-prep/',
    step: '02 / Prepare with purpose',
    title: 'Interview Preparation',
    text: 'Practice system design, leadership, and technical questions across the tools data teams use.',
    linkText: 'Get interview-ready',
  },
  {
    to: '/pde/',
    step: '03 / Go deeper',
    title: 'PDE Certification',
    text: 'Study Google Cloud services with a focused exam plan, cheat sheets, and realistic mock questions.',
    linkText: 'Explore the study plan',
  },
  {
    to: '/notes/',
    step: '04 / Make it yours',
    title: 'My Notes',
    text: 'Keep your learning organized with a study tracker, quick references, and a data engineering glossary.',
    linkText: 'Open your notes',
  },
];

const pipelineSteps = [
  {label: '01', title: 'Ingest', description: 'Bring data in reliably'},
  {label: '02', title: 'Transform', description: 'Shape it for the question'},
  {label: '03', title: 'Deliver', description: 'Make insight useful'},
];

export default function Home(): ReactNode {
  return (
    <Layout
      title="Data Engineering Roadmap"
      description="A practical, structured path to learn data engineering, prepare for interviews, and study for the Google Cloud PDE certification.">
      <header className={styles.hero}>
        <div className={styles.heroInner}>
          <div className={styles.intro}>
            <div className={styles.eyebrow}>Your data engineering field guide</div>
            <h1 className={styles.title}>
              Build your path into <span className={styles.titleAccent}>data engineering.</span>
            </h1>
            <p className={styles.description}>
              A practical place to build strong foundations, get ready for interviews, and grow your
              Google Cloud skills—one clear step at a time.
            </p>
            <div className={styles.actions}>
              <Link className={styles.primaryAction} to="/datastructures/">
                Start with the foundations
              </Link>
              <Link className={styles.secondaryAction} to="/interview-prep/">
                Explore interview prep
              </Link>
            </div>
          </div>

          <aside className={styles.pipeline} aria-label="A simple data pipeline: ingest, transform, deliver">
            <div className={styles.pipelineTop}>
              <p className={styles.visualLabel}>The work, at a glance</p>
              <span className={styles.liveIndicator}>Learning path</span>
            </div>
            <div className={styles.pipelineFlow}>
              {pipelineSteps.map((step, index) => (
                <div key={step.label}>
                  <div className={styles.pipelineNode}>
                    <span className={styles.nodeIcon} aria-hidden="true">
                      {step.label}
                    </span>
                    <span className={styles.nodeCopy}>
                      <span className={styles.nodeTitle}>{step.title}</span>
                      <span className={styles.nodeDescription}>{step.description}</span>
                    </span>
                  </div>
                  {index < pipelineSteps.length - 1 && (
                    <div className={styles.flowConnector} aria-hidden="true" />
                  )}
                </div>
              ))}
            </div>
            <div className={styles.pipelineFoot} role="list" aria-label="Topics covered">
              <span className={styles.tag} role="listitem">Python</span>
              <span className={styles.tag} role="listitem">SQL</span>
              <span className={styles.tag} role="listitem">Spark</span>
              <span className={styles.tag} role="listitem">Cloud</span>
            </div>
          </aside>
        </div>
      </header>

      <main className={styles.content}>
        <div className={styles.contentInner}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.sectionKicker}>A clear route forward</p>
              <h2 className={styles.sectionTitle}>Choose your next step</h2>
            </div>
            <p className={styles.sectionDescription}>
              Start at the beginning or jump straight to the skill you want to build today.
            </p>
          </div>

          <nav className={styles.cardGrid} aria-label="Learning paths">
            {learningPaths.map((path) => (
              <Link className={styles.card} key={path.to} to={path.to}>
                <span className={styles.cardStep}>{path.step}</span>
                <h3 className={styles.cardTitle}>{path.title}</h3>
                <p className={styles.cardText}>{path.text}</p>
                <span className={styles.cardLink}>
                  {path.linkText}
                  <span className={styles.cardArrow} aria-hidden="true">
                    -&gt;
                  </span>
                </span>
              </Link>
            ))}
          </nav>

          <div className={styles.stats} role="list" aria-label="Roadmap highlights">
            <div className={styles.stat} role="listitem">
              <span className={styles.statNumber}>16</span>
              <span className={styles.statLabel}>data structure concepts</span>
            </div>
            <div className={styles.stat} role="listitem">
              <span className={styles.statNumber}>4</span>
              <span className={styles.statLabel}>learning paths</span>
            </div>
            <div className={styles.stat} role="listitem">
              <span className={styles.statNumber}>1</span>
              <span className={styles.statLabel}>practical roadmap</span>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
