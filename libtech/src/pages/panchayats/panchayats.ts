import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';


// import { PanchayatPage } from './panchayat/panchayat'
import { JobcardsPage } from '../jobcards/jobcards'
// import { Panchayat } from '../../models/panchayats'
import { Panchayats } from '../../providers/panchayats'


/*
  Generated class for the Panchayats page.

  See http://ionicframework.com/docs/v2/components/#navigation  for more info on
  Ionic pages and navigation.
*/
@Component({
    selector: 'page-panchayats',
    templateUrl: 'panchayats.html'
})
export class PanchayatsPage {
    panchayats: any; //  Panchayat[];

    constructor(public navCtrl: NavController, public navParams: NavParams, private panchayatList: Panchayats) {
        //        this.panchayats = navParams.data;
        panchayatList.load().subscribe(panchayats => {
            this.panchayats = panchayats;
            //            console.log(panchayats);
        })
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PanchayatsPage');
    }

    gotoJobcardsPage(name: string) {
        this.navCtrl.push(JobcardsPage, { panchayatName: name });
    }
}
