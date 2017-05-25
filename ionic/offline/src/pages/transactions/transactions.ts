import { Component } from '@angular/core';
import {AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { NavController, NavParams } from 'ionic-angular';
import { TransactionPage } from '../transaction/transaction';

@Component({
  selector: 'page-transactions',
  templateUrl: 'transactions.html'
})
export class TransactionsPage {
  jobcardID: string;
  items: AfoListObservable<any[]>;
  transactionPage = TransactionPage;
  constructor(public navCtrl: NavController, public navParams: NavParams, afoDatabase: AngularFireOfflineDatabase) {
    this.jobcardID = this.navParams.get('jobcardName');
    this.items = afoDatabase.list('/transactions/' + this.jobcardID);
  }
}
