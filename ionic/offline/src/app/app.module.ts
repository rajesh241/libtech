import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';
import { AngularFireModule } from 'angularfire2';
import { AngularFireDatabaseModule } from 'angularfire2/database';
import { AngularFireOfflineModule } from 'angularfire2-offline';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { MyApp } from './app.component';

import { HomePage } from '../pages/home/home';
import { JobcardsPage } from '../pages/jobcards/jobcards'
import { TransactionsPage } from '../pages/transactions/transactions'
import { TransactionPage } from '../pages/transaction/transaction'
import { TabsPage } from '../pages/tabs/tabs';

import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

export const firebaseConfig = {
  apiKey: 'AIzaSyBrW6X-PnCpot3Gj4TeknY6_mLwdkIzqNQ',
  authDomain: 'libtech-backend.firebaseapp.com/',
  databaseURL: 'https://libtech-backend.firebaseio.com/',
  storageBucket: 'gs://libtech-backend.appspot.com'
};

@NgModule({
  declarations: [
    MyApp,
    HomePage,
    JobcardsPage,
    TransactionsPage,
    TransactionPage,
    TabsPage
  ],
  imports: [
    AngularFireDatabaseModule,
    AngularFireModule.initializeApp(firebaseConfig),
    AngularFireOfflineModule,
    BrowserModule,
    FormsModule,
    IonicModule.forRoot(MyApp)
  ],
  bootstrap: [IonicApp, MyApp],
  entryComponents: [
    MyApp,
    HomePage,
    JobcardsPage,
    TransactionsPage,
    TransactionPage,
    TabsPage
  ],
  providers: [
    StatusBar,
    SplashScreen,
    {provide: ErrorHandler, useClass: IonicErrorHandler}
  ]
})
export class AppModule {}
