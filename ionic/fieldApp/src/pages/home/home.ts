import { Component } from '@angular/core';

import { NavController } from 'ionic-angular';
import { LoginPage } from '../login/login';
import { PanchayatsPage } from '../panchayats/panchayats'

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
    panchayats: any;
    panchayatSelected = {}; // Placeholder for list of panchayats to fetch
    panchayatsChosen: any;

    constructor(public navCtrl: NavController, private auth: Auth, private panchayatList: Panchayats) {
        if (!this.getUser()) {
            this.navCtrl.push(LoginPage);
        }
        
        panchayatList.load().subscribe(panchayats => {
            this.panchayats = panchayats;
            this.panchayatsChosen = [];
        })
    }

    choosePanchayat(selected, index, panchayat) {
        console.log(selected);
        console.log(panchayat);
        this.panchayatSelected[index] = !this.panchayatSelected[index];
        if(this.panchayatSelected[index]) {
           this.panchayatsChosen.push(panchayat)
           console.log(JSON.stringify(this.panchayatsChosen))
        }
        else {
           var index = this.panchayatsChosen.indexOf(panchayat)
           if (index > -1)
              this.panchayatsChosen.splice(index, 1);
           else
              console.log("Shouldn't reach here " + panchayat)
           console.log(JSON.stringify(this.panchayatsChosen))
       }
    }

    syncPanchayats() {
        
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
