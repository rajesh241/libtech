import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

/*
  Generated class for the Transaction page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-transaction',
  templateUrl: 'transaction.html'
})
export class TransactionPage {
       jobcard: string;
       date: string;
       transaction: string;

  constructor(public navCtrl: NavController, public navParams: NavParams) {
                     this.jobcard = this.navParams.get('jobcard');
                     this.date = this.navParams.get('date');
                     this.transaction = this.navParams.get('transaction');
    }

    ionViewDidLoad() {
                   console.log('ionViewDidLoad TransactionPage');
    }


    goHome() {
        this.navCtrl.popToRoot();
    }
}
