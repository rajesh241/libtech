import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

import { AngularFireModule } from 'angularfire2';
import { AngularFireDatabaseModule } from 'angularfire2/database';
import { AngularFireAuthModule } from 'angularfire2/auth';
import { AngularFireOfflineModule } from 'angularfire2-offline';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';

import { MyApp } from './app.component';
import { ProfilePage } from '../pages/profile/profile'

import { PanchayatsPage } from '../pages/panchayats/panchayats'
import { JobcardsPage } from '../pages/jobcards/jobcards'
import { TransactionsPage } from '../pages/transactions/transactions'
import { TransactionPage } from '../pages/transaction/transaction'

import { ExpandableComponent } from '../components/expandable/expandable';
import { KeysPipe } from '../pipes/keys/keys';
import { AuthProvider } from '../providers/auth/auth';
import { PanchayatsProvider } from '../providers/panchayats/panchayats';
import { JobcardsProvider } from '../providers/jobcards/jobcards';

const firebaseConfig = {
    apiKey: "AIzaSyCv6jE0O5QjsAMK_WzUG2pDvEsIlTZCduY",
    authDomain: "libtech-app.firebaseapp.com",
    databaseURL: "https://libtech-app.firebaseio.com",
    storageBucket: "libtech-app.appspot.com"
}

@NgModule({
    declarations: [
        MyApp,
        PanchayatsPage,
        JobcardsPage,
        TransactionsPage,
        TransactionPage,
        ProfilePage,
	ExpandableComponent,
	KeysPipe
    ],
    imports: [
        AngularFireDatabaseModule,
        AngularFireAuthModule,
        AngularFireModule.initializeApp(firebaseConfig),
        AngularFireOfflineModule,
        BrowserModule,
        IonicModule.forRoot(MyApp)
    ],
    bootstrap: [IonicApp],
    entryComponents: [
        MyApp,
        PanchayatsPage,
        JobcardsPage,
        TransactionsPage,
        TransactionPage,
        ProfilePage
    ],
    providers: [
        StatusBar,
        SplashScreen,
        { provide: ErrorHandler, useClass: IonicErrorHandler },
	AuthProvider,
	PanchayatsProvider,
	JobcardsProvider
    ]
})
export class AppModule { }
