import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFire, FirebaseListObservable } from 'angularfire2';
import { TransactionPage } from '../transaction/transaction';
/*
  Generated class for the Transactions page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
    selector: 'page-transactions',
    templateUrl: 'transactions.html'
})
export class TransactionsPage {
    transactionPage = TransactionPage;
    panchayat: string;
    jobcard: string;
    url: string;
    transactions: FirebaseListObservable<any>;

    constructor(public navCtrl: NavController, public navParams: NavParams, private af: AngularFire) {
        this.panchayat = this.navParams.get('panchayatName');
        this.jobcard = this.navParams.get('jobcardNumber');
        this.url = '/data/' + this.panchayat + '/' + this.jobcard
        this.transactions = af.database.list(this.url);
        console.log(this.url);
        console.log(this.transactions);
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionsPage');
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
