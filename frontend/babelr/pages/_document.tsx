import Document, {
    Html,
    Head,
    Main,
    NextScript,
    DocumentContext,
    DocumentInitialProps,
  } from 'next/document';
import {
    DocumentHeadTags,
    documentGetInitialProps,
  } from '@mui/material-nextjs/v15-pagesRouter';
import { createCustomCache } from 'stylesheets/emotionCache';
import { ReactElement } from 'react';

interface MyDocumentProps extends DocumentInitialProps {
    emotionStyleTags: ReactElement[];
}
  
  
export default class MyDocument extends Document<MyDocumentProps> {
    static async getInitialProps(ctx: DocumentContext) {
      const finalProps = await documentGetInitialProps(ctx, {
        emotionCache: createCustomCache(),
      });
      return finalProps;
    }
  
    render() {
      const { emotionStyleTags, ...rest } = this.props;
  
      return (
        <Html lang="en">
          <Head>
            <DocumentHeadTags emotionStyleTags={emotionStyleTags} {...rest} />
          </Head>
          <body>
            <Main />
            <NextScript />
          </body>
        </Html>
      );
    }
}