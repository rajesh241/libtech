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

    login() {
        this.auth.login(this.email,
            this.password).then((response) => {
                this.navCtrl.pop();
            }).catch((error) => {
                console.log(error);
                alert(error);
            });
    }

    loginWithGoogle() {
        return this.auth.loginWithGoogle().then((response) => {
            this.navCtrl.pop();
        }).catch((error) => {
            console.log(error);
            alert(error);
        });
    }

    loginWithFacebook() {
        return this.auth.loginWithFacebook().then((response) => {
            this.navCtrl.pop();
        }).catch((error) => {
            console.log(error);
            alert(error);
        });
    }

    logout() {
        return this.auth.logout();
    }
}
