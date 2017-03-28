import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFire, FirebaseListObservable } from 'angularfire2';
import { TransactionsPage } from '../transactions/transactions';

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
    panchayatName: string;
    jobcards: FirebaseListObservable<any>;

    constructor(private navCtrl: NavController, private navParams: NavParams, private af: AngularFire) {
        this.panchayatName = this.navParams.get('panchayatName');
        this.jobcards = af.database.list('/jobcard/KURHANI/' + this.panchayatName);
        console.log('/jobcard/KURHANI/' + this.panchayatName);
        console.log(this.jobcards);
    }

    goHome() {
        this.navCtrl.popToRoot();
    }

    gotoJobcard(jobcard: string) {
        this.navCtrl.push(TransactionsPage, { panchayatName: this.panchayatName, jobcardNumber: jobcard });
    }

  ionViewDidLoad() {
    console.log('ionViewDidLoad JobcardsPage');
  }

}
