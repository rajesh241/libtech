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
  constructor(public navCtrl: NavController, afoDatabase: AngularFireOfflineDatabase) {
    this.items = afoDatabase.list('/panchayats');

  }

}
