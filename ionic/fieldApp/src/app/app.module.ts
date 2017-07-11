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
import { HomePage } from '../pages/home/home';
import { LoginPage } from '../pages/login/login';
// Mynk import { SignupPage } from '../pages/signup/signup';
import { PanchayatsPage } from '../pages/panchayats/panchayats'
import { JobcardsPage } from '../pages/jobcards/jobcards'
import { TransactionsPage } from '../pages/transactions/transactions'
import { TransactionPage } from '../pages/transaction/transaction'
import { ProfilePage } from '../pages/profile/profile'

import { Panchayats } from '../providers/panchayats'
import { Auth } from '../providers/auth';
import { ExpandableComponent } from '../components/expandable/expandable';
import { KeysPipe } from '../pipes/keys/keys';

const firebaseConfig = {
    apiKey: "AIzaSyCv6jE0O5QjsAMK_WzUG2pDvEsIlTZCduY",
    authDomain: "libtech-app.firebaseapp.com",
    databaseURL: "https://libtech-app.firebaseio.com",
    storageBucket: "libtech-app.appspot.com"
}

@NgModule({
    declarations: [
        MyApp,
        HomePage,
        LoginPage,
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
        HomePage,
        LoginPage,
        PanchayatsPage,
        JobcardsPage,
        TransactionsPage,
        TransactionPage,
        ProfilePage
    ],
    providers: [
        Panchayats,
        Auth,
        StatusBar,
        SplashScreen,
        { provide: ErrorHandler, useClass: IonicErrorHandler }
    ]
})
export class AppModule { }
