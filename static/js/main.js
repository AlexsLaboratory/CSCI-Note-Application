function deleteNote(id) {
  const url = `note/delete/${id}`;
  fetch(url, {method: "DELETE"}).then(response => console.log(response.status));
}

const deleteModal = document.getElementById("delete-modal");
const deleteNoteButton = deleteModal.getElementsByTagName("button")[0];
let noteId = undefined
document.addEventListener("click", (event) => {
  if (event.target.classList.contains("grid--item__delete")) {
    noteId = event.target.dataset.id
    deleteModal.showModal();
  }
  if (event.target.classList.contains("modal__action")) {
    if (noteId === undefined) return;
    deleteNote(noteId);
    location.reload();
  }
});