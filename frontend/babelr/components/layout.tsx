import Head from "next/head";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Head>
        <title>Dashboard | Babelr</title>
        <meta name="description" content="User dashboard for Babelr" />
      </Head>

      <div>
        {children}
      </div>
    </>
  );
}