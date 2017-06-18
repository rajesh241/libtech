import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { TransactionsPage } from '../transactions/transactions';

@Component({
    selector: 'page-jobcards',
    templateUrl: 'jobcards.html'
})
export class JobcardsPage {
    transactionsPage = TransactionsPage;
    panchayatName: string;
    jobcards: AfoListObservable<any[]>;
    url = '/jobcards/';

    constructor(private navCtrl: NavController, private navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        this.panchayatName = this.navParams.get('panchayatName');
        this.url += this.panchayatName;
        this.jobcards = afoDatabase.list(this.url);
        console.log(this.url);
    }

    goHome() {
        this.navCtrl.popToRoot();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad JobcardsPage');
    }
}
