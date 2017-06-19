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
    rejInv: AfoListObservable<any[]>;
    applicantDetails: AfoListObservable<any[]>;
    //Useful to toggle buttons.  Default is off.
    show: boolean = false;

    constructor(public navCtrl: NavController, public navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        this.panchayat = this.navParams.get('panchayatName');
        this.jobcard = this.navParams.get('jobcardNumber');
        var ptCode = this.jobcard.substring(0, 13);
        var vilCode = this.jobcard.substring(14, 17);
        var h: string[] = this.jobcard.split('_');
        var hhdCode = h[h.length - 1]
        var geoUrl = '/geo/' + ptCode + '/' + vilCode + '/' + hhdCode + '/'
        this.rejInv = afoDatabase.list(geoUrl);

        var appUrl = geoUrl + 'applicants/'
        this.applicantDetails = afoDatabase.list(appUrl);

        this.url = '/transactions/' + this.jobcard
        this.items = afoDatabase.list(this.url);
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionsPage');
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
