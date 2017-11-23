import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { EditPanchayatsPage } from './edit-panchayats';

@NgModule({
  declarations: [
    EditPanchayatsPage,
  ],
  imports: [
    IonicPageModule.forChild(EditPanchayatsPage),
  ],
  exports: [
    EditPanchayatsPage
  ]
})
export class EditPanchayatsPageModule {}
