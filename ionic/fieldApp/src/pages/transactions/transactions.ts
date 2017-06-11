import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { TransactionPage } from '../transaction/transaction';

@Component({
    selector: 'page-transactions',
    templateUrl: 'transactions.html'
})
export class TransactionsPage {
    transactionPage = TransactionPage;
    panchayat: string;
    jobcard: string;
    url: string;
    items: AfoListObservable<any[]>;

    constructor(public navCtrl: NavController, public navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        this.panchayat = this.navParams.get('panchayatName');
        this.jobcard = this.navParams.get('jobcardNumber');
        this.url = '/transactions/' + this.jobcard
        this.items = afoDatabase.list(this.url);
        console.log(this.url);
        console.log(this.items);
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionsPage');
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
