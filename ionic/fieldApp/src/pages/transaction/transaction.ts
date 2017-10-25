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
    selector: 'page-transaction',
    templateUrl: 'transaction.html'
})
export class TransactionPage {
    jobcard: string;
    key: string;
    transaction: string;
    url: string;
    remarks: string;
    createComplaint = false;
    updated = true;
    field: AfoListObservable<any>;
    parent: AfoListObservable<any>;
    loading: Loading;

    constructor(public navCtrl: NavController,
		public navParams: NavParams,
		private afoDatabase: AngularFireOfflineDatabase,
		private loadingCtrl: LoadingController) {
        this.jobcard = this.navParams.get('jobcard');
        this.key = this.navParams.get('key');
        this.transaction = this.navParams.get('transaction');
        this.url = this.navParams.get('url');
        this.parent = this.afoDatabase.list(this.url);
        this.url += '/' + this.key;
        console.log(this.url);
        this.field = this.afoDatabase.list(this.url);
        console.log(this.field);
    }

    update() {
	this.presentSpinner('Updating records...');
        if (this.remarks)
            this.parent.update(this.key, { remarks: this.remarks });
        this.parent.update(this.key, { createComplaint: this.createComplaint });
        this.updated = true;
	this.loading.dismiss();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionPage');
        console.log(this.url);
        console.log(this.jobcard);
        console.log(this.key);
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
