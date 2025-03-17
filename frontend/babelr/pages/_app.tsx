import type { AppProps } from "next/app";
// import Layout from "../components/layout";
import "../stylesheets/globals.css"; // 

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <Component {...pageProps} />
  );
}