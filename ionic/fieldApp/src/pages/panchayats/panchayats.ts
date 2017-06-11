import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';


import { JobcardsPage } from '../jobcards/jobcards'
import { Panchayats } from '../../providers/panchayats'


@Component({
    selector: 'page-panchayats',
    templateUrl: 'panchayats.html'
})
export class PanchayatsPage {
    jobcardsPage = JobcardsPage;
    panchayats: any; //  Panchayat[];

    constructor(public navCtrl: NavController, public navParams: NavParams, private panchayatList: Panchayats) {
        this.panchayats = navParams.data;
        /*
        panchayatList.load().subscribe(panchayats => {
//            this.panchayats = panchayats;
            console.log(panchayats);
        })
        */
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PanchayatsPage');
        this.panchayats = this.navParams.data;
        console.log(this.panchayats);
        console.log(JSON.stringify(this.panchayats))
  }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
