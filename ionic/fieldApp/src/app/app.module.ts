import { NgModule, ErrorHandler } from '@angular/core';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { AngularFireModule } from 'angularfire2';
import { AngularFireOfflineModule } from 'angularfire2-offline';

import { MyApp } from './app.component';
import { HomePage } from '../pages/home/home';
import { LoginPage } from '../pages/login/login';
// Mynk import { SignupPage } from '../pages/signup/signup';
import { PanchayatsPage } from '../pages/panchayats/panchayats'
import { JobcardsPage } from '../pages/jobcards/jobcards'
import { TransactionsPage } from '../pages/transactions/transactions'
import { TransactionPage } from '../pages/transaction/transaction'
import { Panchayats } from '../providers/panchayats'

import { Auth } from '../providers/auth';

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
        TransactionPage
    ],
    imports: [
        IonicModule.forRoot(MyApp),
	AngularFireModule.initializeApp(firebaseConfig),
	AngularFireOfflineModule
    ],
    bootstrap: [IonicApp],
    entryComponents: [
        MyApp,
        HomePage,
        LoginPage,
        PanchayatsPage,
        JobcardsPage,
        TransactionsPage,
        TransactionPage
    ],
    providers: [Panchayats,
        Auth,
        { provide: ErrorHandler, useClass: IonicErrorHandler }]
})
export class AppModule { }
