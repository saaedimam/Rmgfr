import Nav from '@/components/Nav';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <section>
      <Nav />
      {children}
    </section>
  );
}
