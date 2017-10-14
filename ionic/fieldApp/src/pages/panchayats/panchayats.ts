import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { JobcardsPage } from '../jobcards/jobcards';

import { AuthProvider } from '../../providers/auth/auth';
import { PanchayatsProvider } from '../../providers/panchayats/panchayats';

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
    preferredPanchayats: any[];
    panchayatSelected = {};
    panchayatsToSync: any;
    checked = false;
    synced = false;

    constructor(public navCtrl: NavController, private navParams: NavParams, private auth: AuthProvider,
        private panchayatList: PanchayatsProvider, public alertCtrl: AlertController) {
        this.user = this.navParams.data;
        console.log('USER ' + JSON.stringify(this.user));
        this.displayPanchayats = this.user.panchayats;
        this.preferredPanchayats = this.dictToArray(this.displayPanchayats)
        console.log(this.preferredPanchayats);
        console.log('InsideConstructor');
        this.panchayatsToSync = [];
    }

    dictToArray(dict) {
        return Object.keys(dict).map(key => dict[key])
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PanchayatsPage');
        this.panchayats = this.panchayatList.load();
    }

    choosePanchayat(index, panchayat) {
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
        Object.keys(this.panchayats).forEach(panchayatKey => {
            console.log('PANCHAYAT ' + JSON.stringify(panchayatKey));
            alert.addInput({
                type: 'checkbox',
                label: panchayatKey,
                value: panchayatKey,
                checked: panchayatKey in this.displayPanchayats // (this.displayPanchayats.indexOf(panchayatKey) != -1) // 
            });
        });

        alert.addButton('Cancel');
        alert.addButton({
            text: 'Okay',
            handler: data => {
                console.log('Data Handler: ');
                console.log(JSON.stringify(data));
                console.log(this.panchayats);
                this.displayPanchayats = {};
		/*
                this.panchayats.forEach(panchayat => {
                    if (panchayat.panchayatKey in data) this.displayPanchayats[panchayat.panchayatKey] = panchayat
                    else console.log('AKBC')
                }); */
                data.forEach(panchayatKey => { console.log('For this key - ' + panchayatKey); this.displayPanchayats[panchayatKey] = this.panchayats[panchayatKey]; console.log('This panchayat ' + this.displayPanchayats[panchayatKey]) });
                console.log(this.displayPanchayats);
                this.preferredPanchayats = this.dictToArray(this.displayPanchayats)
                console.log(this.preferredPanchayats);
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
