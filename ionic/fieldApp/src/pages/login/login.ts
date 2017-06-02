import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import { Auth } from '../../providers/auth';

@Component({
    selector: 'page-login',
    templateUrl: 'login.html'
})
export class LoginPage {
    email: string;
    password: string;

    constructor(public navCtrl: NavController, public navParams: NavParams, private auth: Auth) { }

    ionViewDidLoad() {
        console.log('ionViewDidLoad LoginPage');
    }
    /*
    login() {
        this.auth.login(this.email, this.password);
        this.navCtrl.pop();
    }

    loginWithGoogle() {
        this.auth.loginWithGoogle();
        this.navCtrl.pop();
    }
    */
    loginWithFacebook() {
        this.auth.loginWithFacebook();
        this.navCtrl.pop();
    }

    logout() {
        return this.auth.logout();
    }
}
