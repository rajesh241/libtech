import { Component } from '@angular/core';
import {AngularFireOfflineDatabase, AfoObjectObservable } from 'angularfire2-offline/database';
import { NavController, NavParams } from 'ionic-angular';

@Component({
  selector: 'page-transaction',
  templateUrl: 'transaction.html'
})
export class TransactionPage {
  transactionID: string;
  jobcardID: string;
  item: AfoObjectObservable<any>;
  constructor(public navCtrl: NavController, public navParams: NavParams, afoDatabase: AngularFireOfflineDatabase) {
    this.transactionID = this.navParams.get('transactionName');
    this.jobcardID = this.transactionID.split(":")[0]
    this.item = afoDatabase.object('/transactions/' + this.jobcardID + '/' + this.transactionID);
    console.log(this.item)
  }
}
