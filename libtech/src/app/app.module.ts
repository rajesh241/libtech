import { NgModule, ErrorHandler } from '@angular/core';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { AngularFireModule } from 'angularfire2';

import { MyApp } from './app.component';
import { HomePage } from '../pages/home/home';
import { PanchayatsPage } from '../pages/panchayats/panchayats'
import { JobcardsPage } from '../pages/jobcards/jobcards'
import { TransactionsPage } from '../pages/transactions/transactions'
import { TransactionPage } from '../pages/transaction/transaction'
import { Panchayats } from '../providers/panchayats'

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
        PanchayatsPage,
        JobcardsPage,
        TransactionsPage,
        TransactionPage
    ],
    imports: [
        AngularFireModule.initializeApp(firebaseConfig),
        IonicModule.forRoot(MyApp)
    ],
    bootstrap: [IonicApp],
    entryComponents: [
        MyApp,
        HomePage,
        PanchayatsPage,
        JobcardsPage,
        TransactionsPage,
        TransactionPage
    ],
    providers: [Panchayats,
        { provide: ErrorHandler, useClass: IonicErrorHandler }]
})
export class AppModule { }
