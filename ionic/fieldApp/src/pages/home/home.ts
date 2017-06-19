import { Component } from '@angular/core';

import { NavController } from 'ionic-angular';
import { LoginPage } from '../login/login';
import { PanchayatsPage } from '../panchayats/panchayats'
import { JobcardsPage } from '../jobcards/jobcards'
import { ProfilePage } from '../profile/profile'

import { Auth } from '../../providers/auth';
import { Panchayats } from '../../providers/panchayats'

import { AlertController } from 'ionic-angular';

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    user: any;
    loginPage = LoginPage;
    panchayatsPage = PanchayatsPage;
    jobcardsPage = JobcardsPage;
    profilePage = ProfilePage;
    panchayats: any;
    displayPanchayats: any;
    panchayatSelected = {};
    panchayatsChosen: any;
    checked = false;
    synced = false;

    constructor(public navCtrl: NavController, private auth: Auth,
        private panchayatList: Panchayats,
        public alertCtrl: AlertController) {
        this.user = this.auth.getUser();
        if (!this.user) {
            this.navCtrl.push(LoginPage);
        }
        console.log('After Login');
        // Hard Refresh - window.location.reload(false)


        this.panchayatsChosen = [];
        this.panchayats = panchayatList.load();
    }

    choosePanchayat(selected, index, panchayat) {
        this.checked = true;
        this.synced = false;
        this.panchayatSelected[index] = !this.panchayatSelected[index];
        if (this.panchayatSelected[index]) {
            this.panchayatsChosen.push(panchayat)
            // console.log(JSON.stringify(this.panchayatsChosen))
        }
        else {
            var index = this.panchayatsChosen.indexOf(panchayat)
            if (index > -1)
                this.panchayatsChosen.splice(index, 1);
            else
                console.log("Shouldn't reach here " + panchayat)
            // console.log(JSON.stringify(this.panchayatsChosen))
        }
    }

    syncPanchayats() {
        this.panchayatList.sync(this.panchayatsChosen);
        this.synced = true;
    }

    getUser() {
        this.user = this.auth.getUser();
        return this.user;
    }

    logout() {
        this.auth.logout();
    }

    editPanchayaList() {
        let alert = this.alertCtrl.create();
        alert.setTitle('Select the Panchayats:');

        this.panchayats.subscribe(snapshots => {
            snapshots.forEach(snapshot => {
                var panchayat = snapshot['$key']; // FIXME .toUpperCase();
                // console.log(panchayat);
                alert.addInput({
                    type: 'checkbox',
                    label: panchayat,
                    value: panchayat,
                    checked: false
                });
            });
        });

        alert.addButton('Cancel');
        alert.addButton({
            text: 'Okay',
            handler: data => {
                this.panchayatsChosen = data; // .join(", ") //  .map(function (currentValue, index, arr) { return currentValue; });
                console.log('Checkbox data:', data);
                console.log('Boxed data:', this.panchayatsChosen);
                this.auth.update(this.panchayatsChosen);
            }
        });
        alert.present();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad HomePage');
    }

    ionViewDidEnter() {
        console.log('ionViewDidEnter HomePage');
        this.displayPanchayats = this.auth.fetch();
        console.log('Yippie!' + this.displayPanchayats);
    }
}
