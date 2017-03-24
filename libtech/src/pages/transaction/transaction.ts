import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

@Component({
    selector: 'page-transaction',
    templateUrl: 'transaction.html'
})
export class TransactionPage {
    jobcard: string;
    date: string;
    transaction: string;

    constructor(public navCtrl: NavController, public navParams: NavParams) {
        this.jobcard = this.navParams.get('jobcard');
        this.date = this.navParams.get('date');
        this.transaction = this.navParams.get('transaction');
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionPage');
    }


    goHome() {
        this.navCtrl.popToRoot();
    }
}
