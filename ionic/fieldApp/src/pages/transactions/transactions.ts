import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';

@IonicPage()
@Component({
    selector: 'page-transactions',
    templateUrl: 'transactions.html'
})
export class TransactionsPage {
    transactionPage = 'TransactionPage';
    panchayatSlug: string;
    jobcard: string;
    url: string;
    phone: string;
    updated = true;
    items: AfoListObservable<any[]>;
    applicantDetails: AfoListObservable<any[]>;
    //Useful to toggle buttons.  Default is off.
    show: boolean = false;
    

    constructor(public navCtrl: NavController, public navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        console.log('Inside Transactions Constructor');
        this.jobcard = this.navParams.get('jobcard').replace('/', '_');
        console.log(this.jobcard);
	
        let appUrl = this.navParams.get('url') + '/applicants/';
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
