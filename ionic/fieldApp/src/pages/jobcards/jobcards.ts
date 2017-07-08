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
    panchayatSlug: string;
    // jobcardCode: string;
    jobcards: AfoListObservable<any[]>;
    url = '/geo/';
    // jobcardSlug: string;

    constructor(private navCtrl: NavController, private navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        this.panchayatSlug = this.navParams.get('panchayatSlug');
        // this.jobcardCode = this.navParams.get('jobcardCode');
        // this.url += this.jobcardCode;
        // this.jobcards = afoDatabase.list(this.url);
        console.log(this.url + this.panchayatSlug); // + this.jobcardCode);
        this.jobcards = afoDatabase.list(this.url, {
            query: {
                orderByChild: 'panchayatSlug',
                equalTo: this.panchayatSlug
            }
        });
    }

    goHome() {
        this.navCtrl.popToRoot();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad JobcardsPage');
    }
}
