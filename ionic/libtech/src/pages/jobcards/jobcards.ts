import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

// import { AngularFire, FirebaseListObservable } from 'angularfire2';
import { TransactionsPage } from '../transactions/transactions';
import {
  AngularFireOffline,
    AfoListObservable,
      AfoObjectObservable } from 'angularfire2-offline';
/*
  Generated class for the Jobcards page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
    selector: 'page-jobcards',
    templateUrl: 'jobcards.html'
})
export class JobcardsPage {
    transactionsPage = TransactionsPage;
    panchayatName: string;
    // jobcards: FirebaseListObservable<any>;
    jobcards: AfoListObservable<any[]>;

    constructor(private navCtrl: NavController, private navParams: NavParams, private afo: AngularFireOffline) {
        this.panchayatName = this.navParams.get('panchayatName');
        this.jobcards = afo.database.list('/jobcard/KURHANI/' + this.panchayatName);
        console.log('/jobcard/KURHANI/' + this.panchayatName);
        console.log(this.jobcards);
    }

    goHome() {
        this.navCtrl.popToRoot();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad JobcardsPage');
    }
}
