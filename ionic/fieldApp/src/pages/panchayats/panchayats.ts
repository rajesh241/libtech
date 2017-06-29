import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { JobcardsPage } from '../jobcards/jobcards'

import { Auth } from '../../providers/auth';
import { Panchayats } from '../../providers/panchayats'

import { AlertController } from 'ionic-angular';

@Component({
    selector: 'page-panchayats',
    templateUrl: 'panchayats.html'
})
export class PanchayatsPage {
    jobcardsPage = JobcardsPage;
    panchayats: any;
    user: any;
    displayPanchayats: any;
    panchayatSelected = {};
    panchayatsToSync: any;
    checked = false;
    synced = false;

    constructor(public navCtrl: NavController, private navParams: NavParams, private auth: Auth,
        private panchayatList: Panchayats, public alertCtrl: AlertController) {
        this.user = this.navParams.data;
        this.panchayatsToSync = [];
        console.log('InsideConstructor');
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PanchayatsPage');
        console.log('USER ' + JSON.stringify(this.user));
        this.displayPanchayats = this.user.panchayats.split(', ');
        console.log(this.displayPanchayats);
        this.panchayats = this.panchayatList.load();
        console.log('PANCHAYATS ' + JSON.stringify(this.panchayats));
    }

    choosePanchayat(selected, index, panchayat) {
        this.checked = true;
        this.synced = false;
        this.panchayatSelected[index] = !this.panchayatSelected[index];
        if (this.panchayatSelected[index]) {
            // if (this.panchayatsToSync.indexOf(panchayat) == -1)
            this.panchayatsToSync.push(panchayat);
            // console.log(JSON.stringify(this.panchayatsToSync))
        }
        else {
            var index = this.panchayatsToSync.indexOf(panchayat)
            if (index > -1)
                this.panchayatsToSync.splice(index, 1);
            else
                console.log("Shouldn't reach here " + panchayat)
            // console.log(JSON.stringify(this.panchayatsToSync))
        }
    }

    editPanchayaList() {
        let alert = this.alertCtrl.create();
        alert.setTitle('Select the Panchayats:');

        this.panchayats = this.panchayatList.load();
        this.panchayats.forEach(panchayat => {
            //  console.log('PANCHAYAT ' + panchayat);
            alert.addInput({
                type: 'checkbox',
                label: panchayat,
                value: panchayat,
                checked: (this.displayPanchayats.indexOf(panchayat) != -1)
            });
        });

        alert.addButton('Cancel');
        alert.addButton({
            text: 'Okay',
            handler: data => {
                this.displayPanchayats = data;
                this.auth.update(this.displayPanchayats);
            }
        });
        alert.present();
    }

    syncPanchayats() {
        this.panchayatList.sync(this.panchayatsToSync);
        this.synced = true;
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
