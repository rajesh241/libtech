import { Component } from '@angular/core';
import { IonicPage,
	 NavController,
	 NavParams,
	 LoadingController,
	 Loading
       } from 'ionic-angular';

import { AuthProvider } from '../../providers/auth/auth';
import { PanchayatsProvider } from '../../providers/panchayats/panchayats';

import { AlertController } from 'ionic-angular';

@IonicPage()
@Component({
    selector: 'page-panchayats',
    templateUrl: 'panchayats.html'
})
export class PanchayatsPage {
    jobcardsPage = 'JobcardsPage';
    panchayats: any;
    user: any;
    userPanchayats: any;
    preferredPanchayats: any[];
    panchayatSelected = {};
    panchayatsToSync: any;
    checked = false;
    synced = false;
    loading:Loading;

    constructor(public navCtrl: NavController,
		private navParams: NavParams,
		private auth: AuthProvider,
		private panchayatsProvider: PanchayatsProvider,
		private alertCtrl: AlertController,
		private loadingCtrl: LoadingController) {
        this.user = this.navParams.data;
        console.log('USER ' + JSON.stringify(this.user));
        this.userPanchayats = this.user.panchayats;
        this.preferredPanchayats = this.dictToArray(this.userPanchayats)
        console.log(this.preferredPanchayats);
        console.log('InsideConstructor');
        this.panchayatsToSync = [];
    }

    dictToArray(dict) {
        return Object.keys(dict).map(key => dict[key])
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PanchayatsPage');
        // this.panchayats = this.panchayatsProvider.load();  FIXME
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

        this.panchayats = this.panchayatsProvider.load();
        Object.keys(this.panchayats).forEach(panchayatKey => {
            console.log('PANCHAYAT ' + JSON.stringify(panchayatKey));
            alert.addInput({
                type: 'checkbox',
                label: panchayatKey,
                value: panchayatKey,
                checked: panchayatKey in this.userPanchayats // (this.userPanchayats.indexOf(panchayatKey) != -1) // 
            });
        });

        alert.addButton('Cancel');
        alert.addButton({
            text: 'Okay',
            handler: data => {
                console.log('Data Handler: ');
                console.log(JSON.stringify(data));
                console.log(this.panchayats);
                this.userPanchayats = {};
		/*
                this.panchayats.forEach(panchayat => {
                    if (panchayat.panchayatKey in data) this.userPanchayats[panchayat.panchayatKey] = panchayat
                    else console.log('AKBC')
                }); */
                data.forEach(panchayatKey => { console.log('For this key - ' + panchayatKey); this.userPanchayats[panchayatKey] = this.panchayats[panchayatKey]; console.log('This panchayat ' + this.userPanchayats[panchayatKey]) });
                console.log(this.userPanchayats);
                this.preferredPanchayats = this.dictToArray(this.userPanchayats)
                console.log(this.preferredPanchayats);
                this.auth.update(this.userPanchayats);
            }
        });
        alert.present();
    }

    presentSpinner(msg) {
	this.loading = this.loadingCtrl.create({
	    content: msg,
	    dismissOnPageChange: true,
	});

	this.loading.present();
    }

    editPanchayatPage() {
	this.navCtrl.push('EditPanchayatsPage', this.user);
    }
        
    syncPanchayats() {
	this.presentSpinner('Syncing Panchayats...');
        this.panchayatsProvider.sync(this.panchayatsToSync);
        this.synced = true;
	this.loading.dismiss();
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
