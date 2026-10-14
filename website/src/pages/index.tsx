import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

const cards = [
  {
    to: '/datastructures/',
    title: 'Data Structures',
    text: 'Lists to graphs and tries: concept summary, Big-O table, use cases and runnable Python.',
  },
  {
    to: '/interview-prep/',
    title: 'Interview Preparation',
    text: 'Round-by-round guide, system design, leadership, and Q&A plus coding for each tech stack.',
  },
  {
    to: '/pde/',
    title: 'PDE Certification',
    text: 'Google Cloud Professional Data Engineer study plan, service cheat sheet and mock question banks.',
  },
  {
    to: '/notes/',
    title: 'My Notes',
    text: 'Study tracker, quick references and glossary.',
  },
];

export default function Home(): ReactNode {
  return (
    <Layout title="Data Engineering Roadmap" description="Data engineering learning roadmap">
      <header style={{padding: '4rem 1rem 2rem', textAlign: 'center'}}>
        <h1 style={{fontSize: '3rem'}}>Data Engineering Roadmap</h1>
        <p style={{fontSize: '1.2rem'}}>
          Suggested order: Data Structures, then Interview Preparation, then PDE Certification. Keep notes as you go.
        </p>
      </header>
      <main
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.5rem',
          maxWidth: 1100,
          margin: '0 auto 4rem',
          padding: '0 1rem',
        }}>
        {cards.map((c) => (
          <Link
            key={c.to}
            to={c.to}
            style={{
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: 8,
              padding: '1.5rem',
              textDecoration: 'none',
              color: 'inherit',
            }}>
            <h2>{c.title}</h2>
            <p>{c.text}</p>
          </Link>
        ))}
      </main>
    </Layout>
  );
}
