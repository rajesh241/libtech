import { Component } from '@angular/core';
import {AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { NavController } from 'ionic-angular';
import { JobcardsPage } from '../jobcards/jobcards';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {
  jobcardsPage = JobcardsPage;
  items: AfoListObservable<any[]>;
  jobcards: AfoListObservable<any[]>;
  panchayat = {}
  constructor(public navCtrl: NavController, private afoDatabase: AngularFireOfflineDatabase) {
    this.items = this.afoDatabase.list('/panchayats');
    }

  syncForm() {
    console.log(this.panchayat);
    var url = '/jobcards/' + this.panchayat;
    console.log(url);
    this.jobcards = this.afoDatabase.list('/jobcards/' + this.panchayat);
    this.jobcards.subscribe(jobcards => {
      jobcards.forEach(element => {
        console.log(element['$key']);
        this.afoDatabase.list('/transactions/' + element['$key']);
    });
   });
  }

}
