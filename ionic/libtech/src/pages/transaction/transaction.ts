import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import { AngularFire, FirebaseListObservable } from 'angularfire2';
/*import {
  AngularFireOffline,
    AfoListObservable,
    AfoObjectObservable } from 'angularfire2-offline';*/

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
    field: FirebaseListObservable<any>;


    constructor(public navCtrl: NavController, public navParams: NavParams, private af: AngularFire) {
        this.jobcard = this.navParams.get('jobcard');
        this.date = this.navParams.get('date');
        this.transaction = this.navParams.get('transaction');
        this.url = this.navParams.get('url') + '/' + this.date;
        this.index = String(this.navParams.get('index'));
        console.log(this.url);
        this.field = this.af.database.list(this.url);
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
