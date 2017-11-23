import { Component } from '@angular/core';
import { IonicPage,
	 NavController,
	 NavParams,
	 LoadingController,
	 Loading
       } from 'ionic-angular';

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
    loading: Loading;

    constructor(public navCtrl: NavController,
		public navParams: NavParams,
		private afoDatabase: AngularFireOfflineDatabase,
	        private loadingCtrl: LoadingController) {
        console.log('Inside Transactions Constructor');
        this.jobcard = this.navParams.get('jobcard').replace('/', '_');
        console.log(this.jobcard);
	
        let appUrl = this.navParams.get('url') + '/applicants/';
        this.applicantDetails = afoDatabase.list(appUrl);

        this.url = '/transactions/' + this.jobcard
        this.items = afoDatabase.list(this.url);
    }

    update(index) {
	this.presentSpinner('Syncing Panchayats...');
        if (this.phone) {
	    let date = new Date().getTime()
	    this.applicantDetails.update(String(index), { phone: this.phone, timeStamp: date });
	}
        this.updated = true;
	this.loading.dismiss();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionsPage');
    }

    presentSpinner(msg) {
	this.loading = this.loadingCtrl.create({
	    content: msg,
	    dismissOnPageChange: true,
	});

	this.loading.present();
    }
    
    goHome() {
        this.navCtrl.popToRoot();
    }
}
