import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';

@Component({
    selector: 'page-transaction',
    templateUrl: 'transaction.html'
})
export class TransactionPage {
    jobcard: string;
    date: string;
    transaction: string;
    url: string;
    index: string;
    remarks: string;
    createComplaint = false;
    updated = true;
    field: AfoListObservable<any>;


    constructor(public navCtrl: NavController, public navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
        this.jobcard = this.navParams.get('jobcard');
        this.date = this.navParams.get('date');
        this.transaction = this.navParams.get('transaction');
        this.url = this.navParams.get('url') + '/' + this.date;
        this.index = String(this.navParams.get('index'));
        console.log(this.url);
        this.field = this.afoDatabase.list(this.url);
        console.log(this.field);
    }

    update() {
        if (this.remarks)
            this.field.update(this.index, { remarks: this.remarks });
        this.field.update(this.index, { createComplaint: this.createComplaint });
        this.updated = true;
        alert("Updated Record");
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionPage');
    }


    goHome() {
        this.navCtrl.popToRoot();
    }
}
