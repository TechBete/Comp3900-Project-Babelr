import type { AppProps } from "next/app";
import { AppCacheProvider } from '@mui/material-nextjs/v15-pagesRouter';

import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'

import "../stylesheets/globals.css"; // 
import Head from "next/head";

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AppCacheProvider>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Head>
          <link 
            rel="stylesheet" 
            href="https://fonts.googleapis.com/icon?family=Material+Icons"
          />
        </Head>
        <Component {...pageProps} />
      </LocalizationProvider>
    </AppCacheProvider>
  );
}