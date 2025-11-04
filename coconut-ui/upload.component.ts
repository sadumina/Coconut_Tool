// upload(event: Event): void {
//   const input = event.target as HTMLInputElement;

//   if (!input.files || input.files.length === 0) {
//     console.warn("No file selected");
//     return;
//   }

//   const file = input.files[0];   // ✅ Safe now
//   const formData = new FormData();
//   formData.append("file", file);

//   this.api.uploadPDF(formData).subscribe((res: any) => {
//     this.message = `Saved ${res.saved_to_db} new records ✅`;
//   });
// }
