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
    panchayatSlug: string;
    jobcard: string;
    jobcardSlug: string;
    url: string;
    phone: string;
    updated = true;
    items: AfoListObservable<any[]>;
    rejInv: AfoListObservable<any[]>;
    applicantDetails: AfoListObservable<any[]>;
    //Useful to toggle buttons.  Default is off.
    show: boolean = false;

    constructor(public navCtrl: NavController, public navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        console.log('Inside Transactions Constructor');
        this.panchayatSlug = this.navParams.get('panchayatSlug');
        this.jobcardSlug = this.navParams.get('jobcardSlug');
        this.jobcard = this.jobcardSlug.replace('/', '_');
        console.log(this.panchayatSlug)
        console.log(this.jobcard);
        console.log(this.jobcardSlug);

        var ptCode = this.jobcard.substring(0, 13);
        var vilCode = this.jobcard.substring(14, 17);
        var h: string[] = this.jobcard.split('_');
        var hhdCode = h[h.length - 1]
        var geoUrl = '/geo/' + ptCode + '/' + vilCode + '/' + hhdCode + '/'
        // console.log('Values ' + this.jobcard, ptCode, vilCode, h, hhdCode, geoUrl);
        console.log(geoUrl);

        this.rejInv = afoDatabase.list(geoUrl);

        var appUrl = geoUrl + 'applicants/'
        this.applicantDetails = afoDatabase.list(appUrl);

        this.url = '/transactions/' + this.jobcard
        this.items = afoDatabase.list(this.url);
    }

    update(index) {
        if (this.phone)
            this.applicantDetails.update(String(index), { phone: this.phone });
        this.updated = true;
        alert("Updated Phone");
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionsPage');
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
