import { Component } from '@angular/core';
import {AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { NavController, NavParams } from 'ionic-angular';
import { TransactionsPage } from '../transactions/transactions';

@Component({
  selector: 'page-jobcards',
  templateUrl: 'jobcards.html'
})
export class JobcardsPage {
  transactionsPage = TransactionsPage;
  panchayatName: string;
  items: AfoListObservable<any[]>;
  constructor(public navCtrl: NavController, public navParams: NavParams, afoDatabase: AngularFireOfflineDatabase) {
    this.panchayatName = this.navParams.get('panchayatName');
    this.items = afoDatabase.list('/jobcards/' + this.panchayatName);
  }
}
