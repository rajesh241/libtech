import { Component } from '@angular/core';

import { NavController } from 'ionic-angular';
import { LoginPage } from '../login/login';
import { PanchayatsPage } from '../panchayats/panchayats'
import { JobcardsPage } from '../jobcards/jobcards'
import { ProfilePage } from '../profile/profile'

import { Auth } from '../../providers/auth';
import { Panchayats } from '../../providers/panchayats'

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
    panchayatSelected = {};
    panchayatsChosen: any;
    checked = false;
    synced = false;

    constructor(public navCtrl: NavController, private auth: Auth, private panchayatList: Panchayats) {
        if (!this.getUser()) {
            this.navCtrl.push(LoginPage);
        }

        this.panchayatsChosen = [];
        this.panchayats = panchayatList.fetch(this.user);
        console.log(this.panchayats);
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

    ionViewDidLoad() {
        console.log('ionViewDidLoad HomePage');
    }
}
