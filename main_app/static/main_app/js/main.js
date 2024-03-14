let timers = {};
let timerStatus = {};

function addActiveTask() {
  let activeTasksDiv = document.querySelector('.active__tasks');
  let listItem = activeTasksDiv.querySelector('li.active__task');

  if (listItem) {
    let currPopup = document.getElementById("warning-popup");
    popupOpen(currPopup);
    return;
  }

  let form = document.getElementById("tasks__form");
  let taskName = form.querySelector(".input").value;

  if (taskName.trim() === "") {
    alert("Введите название задачи");
    return;
  }

  // Собираем данные формы
  let formData = new FormData(form);
  formData.append('task_name', taskName);

  // Отправляем асинхронный запрос на сервер
  fetch(form.action, {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return response.json();
    })
    .then(data => {
      // Обработка ответа от сервера
      let task_already_present = data.task_already_present;
      if (task_already_present) {
        let currPopup = document.getElementById("warning-popup");
        popupOpen(currPopup);
        return;
      }

      let taskList = document.querySelector(".tasks__block__list");
      let taskId = data.task_id;
      let start = data.start;

      let taskLi = document.createElement("li");
      taskLi.classList.add("tasks__block__list__item", "list__item", "active__task");

      let innerA = document.createElement("a");
      innerA.href = "#";
      innerA.classList.add("list__item__link");
      innerA.setAttribute("data-item-id", taskId);

      let innerTitleDiv = document.createElement("div");
      innerTitleDiv.className = "list__item__title";
      innerTitleDiv.textContent = taskName;

      let innerStrendDiv = document.createElement("div");
      innerStrendDiv.className = "list__item__strend";
      innerStrendDiv.textContent = `${start} - ${start}`;

      let innerStrendTimeDiv = document.createElement("div");
      innerStrendTimeDiv.className = "list__item__sepndtime";

      let pElement = document.createElement("p");
      pElement.textContent = "00:00";

      let iElement = document.createElement("i");
      iElement.classList.add("_icon-stop-circle");
      iElement.setAttribute("onclick", "finishActiveTask()");

      innerStrendTimeDiv.appendChild(pElement);
      innerStrendTimeDiv.appendChild(iElement)

      innerA.appendChild(innerTitleDiv);
      innerA.appendChild(innerStrendDiv);
      innerA.appendChild(innerStrendTimeDiv);

      taskLi.appendChild(innerA);

      taskList.appendChild(taskLi);

      let firstTask = taskList.firstChild;
      if (firstTask !== null) {
        // Если есть, вставляем новый элемент перед первым элементом в списке
        taskList.insertBefore(taskLi, firstTask);
      } else {
        // Если список пуст, просто добавляем новый элемент в конец
        taskList.appendChild(taskLi);
      }

      let activeTask = document.querySelector(".active__task");
      let timerDiv = activeTask.querySelector(".list__item__sepndtime p");
      // Стартуем секундомер для новой задачи
      startTimer(timerDiv);
    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });

  form.querySelector(".input").value = "";

}

function finishActiveTask() {

  let taskId = document.querySelector(".active__task a").getAttribute("data-item-id");

  let timeCurrent = document.querySelector(".active__task .list__item__sepndtime p").textContent;
  let timeCurrentSplitted = timeCurrent.split(":");
  let minutesCurrent = timeCurrentSplitted[0].trim();
  let minutesCurrentInt = parseInt(minutesCurrent, 10);

  if (minutesCurrentInt < 1) {
    popupOpen(document.getElementById("less-than-minute-popup"));
    return;
  }

  fetch("/finish-active-task/", {
    method: "POST",
    body: JSON.stringify({ taskId }),
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return response.json();
    })
    .then(data => {
      console.log('hi');
      let task_duration = data.task_duration;

      let activeTask = document.querySelector(".active__task");
      let clonedElement = activeTask.cloneNode(true);
      activeTask.remove();
      clonedElement.classList.remove("active__task");
      clonedElement.classList.add("done", "with__time");
      clonedElement.querySelector("a").setAttribute("href", "#edit-completed-task-popup");
      clonedElement.querySelector("a").classList.add("popup-link");

      clonedElement.querySelector(".list__item__sepndtime").textContent = formatDuration(task_duration);

      let ul = document.getElementById("today__tasks__block__list");
      ul.appendChild(clonedElement);

      sortAndGetTotalTime()

      clonedElement.querySelector(".popup-link").addEventListener("click", function (e) {
        e.preventDefault();
        const popupName = this.getAttribute('href').replace('#', '');
        const currPopup = document.getElementById(popupName);

        if (this.hasAttribute('data-item-id')) {
          const itemId = this.getAttribute('data-item-id');
          const hiddenInput = currPopup.querySelector("[name='taskId']");
          hiddenInput.value = itemId;
          hiddenInput.dispatchEvent(new Event('change'));
        }

        popupOpen(currPopup)
      });

    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function addPendingTask() {
  let form = document.getElementById("tasks__form");
  let taskName = form.querySelector(".input").value;

  if (taskName.trim() === "") {
    alert("Введите название задачи");
    return;
  }

  // Собираем данные формы
  let formData = new FormData(form);
  formData.append('task_name', taskName);

  // Отправляем асинхронный запрос на сервер
  fetch("/add-pending-task/", {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return response.json();
    })
    .then(data => {
      // Обработка ответа от сервера
      let taskList = document.querySelector(".tasks__block__list");
      let taskId = data.task_id;

      let taskLi = document.createElement("li");
      taskLi.classList.add("tasks__block__list__item", "list__item", "waiting-task");

      let innerA = document.createElement("a");
      innerA.href = "#edit-task-popup";
      innerA.classList.add("list__item__link", "popup-link");
      innerA.setAttribute("data-item-id", taskId);

      let innerTitleDiv = document.createElement("div");
      innerTitleDiv.className = "list__item__title";
      innerTitleDiv.textContent = taskName;

      let innerHoverDiv = document.createElement("div");
      innerHoverDiv.className = "list__item__run";

      let iElement = document.createElement("i");
      iElement.classList.add("_icon-play");
      iElement.addEventListener("click", makePendingTaskActive);

      innerHoverDiv.appendChild(iElement);

      innerA.appendChild(innerTitleDiv);
      innerA.appendChild(innerHoverDiv);

      taskLi.appendChild(innerA);

      taskList.appendChild(taskLi);

      innerA.addEventListener("click", bindTaskWithPopup);

    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });

  form.querySelector(".input").value = "";

}

function saveEditableTask() {
  let form = document.getElementById("edit__pending__popup__form");
  let taskName = form.querySelector(".input").value;


  if (taskName.trim() === "") {
    alert("Введите название задачи");
    return;
  }

  // Собираем данные формы
  let formData = new FormData(form);
  formData.append('task_name', taskName);

  console.log(taskName);

  // Отправляем асинхронный запрос на сервер
  fetch("/edit-pending-task/", {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => response.json())
    .then(data => {
      let task_id = data.task_id;
      let tasksList = document.getElementById('upper__tasks__block__list');
      let listItems = tasksList.querySelectorAll(".tasks__block__list__item a");

      listItems.forEach(function (item) {
        // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
        if (item.hasAttribute('data-item-id') && item.getAttribute('data-item-id') == task_id) {
          // Добавление класса "highlight" к текущему элементу <li>
          let divTitle = item.querySelector(".list__item__title");
          divTitle.textContent = taskName;

          let popupId = item.getAttribute('href').replace('#', '');
          let popupActive = document.getElementById(popupId);
          popupActive.querySelector("input[name='task_name']").value = "";
          popupClose(popupActive);

        }
      });
    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function addCompletedTask() {
  let form = document.getElementById("add__completed__task__popup__form");

  let taskName = form.querySelector(".task__name").value;
  if (taskName.trim() === "") {
    alert("Введите название задачи");
    return;
  }

  let taskStart = form.querySelector(".task__start").value;
  let taskEnd = form.querySelector(".task__end").value;

  var timeFormat = /^([01]\d|2[0-3]):([0-5]\d)$/;
  if ((timeFormat.test(taskStart) && timeFormat.test(taskEnd)) || (taskStart === "" && taskEnd === "")) {
    if (taskStart === "" && taskEnd === "") {
      console.log('Правильное время');
    } else {
      // Если формат правильный, разбиваем строку на часы и минуты
      var taskStartSplit = taskStart.split(':');
      var startHours = parseInt(taskStartSplit[0], 10);
      var startMinutes = parseInt(taskStartSplit[1], 10);

      // Создаем объект времени с сегодняшней датой и введенным временем
      var startTimeObj = new Date();
      startTimeObj.setHours(startHours);
      startTimeObj.setMinutes(startMinutes);

      var taskEndSplit = taskEnd.split(':');
      var endHours = parseInt(taskEndSplit[0], 10);
      var endMinutes = parseInt(taskEndSplit[1], 10);

      // Создаем объект времени с сегодняшней датой и введенным временем
      var endTimeObj = new Date();
      endTimeObj.setHours(endHours);
      endTimeObj.setMinutes(endMinutes);

      if (startTimeObj >= endTimeObj) {
        alert('Время окончания задачи должно превышать время начала!');
        return;
      } else {
        console.log('Правильное время');
      }
    }
  } else {
    alert('Неправильный формат времени!');
    return;
  }

  // Собираем данные формы
  let formData = new FormData(form);
  formData.append('task_name', taskName);
  formData.append('task_start_time', taskStart);
  formData.append('task_end_time', taskEnd);

  // Отправляем асинхронный запрос на сервер
  fetch("/add-completed-task/", {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => response.json())
    .then(data => {

      let taskId = data.task_id;
      let taskStartTime = data.task_start_time;
      let taskEndTime = data.task_end_time;
      let task_duration = data.task_duration;

      let tasksList = document.getElementById('today__tasks__block__list');

      let innerLi = document.createElement("li");
      innerLi.classList.add("tasks__block__list__item", "list__item", "done");

      let innerA = document.createElement("a");
      innerA.href = "#edit-completed-task-popup";
      innerA.classList.add("list__item__link", "popup-link");
      innerA.setAttribute("data-item-id", taskId);

      let innerTitleDiv = document.createElement("div");
      innerTitleDiv.className = "list__item__title";
      innerTitleDiv.textContent = taskName;

      let innerStrendDiv = document.createElement("div");
      let innerSpendTimeDiv = document.createElement("div");

      if (taskStartTime && taskEndTime) {
        console.log('not null');

        innerLi.classList.add("with__time");

        function addLeadingZero(num) {
          return (num < 10 ? '0' : '') + num;
        }

        var taskStartTimeFormatted = new Date(taskStartTime);
        var taskEndTimeFormatted = new Date(taskEndTime);

        var taskStartHours = taskStartTimeFormatted.getHours();
        var taskStartMinutes = taskStartTimeFormatted.getMinutes();

        var taskEndHours = taskEndTimeFormatted.getHours();
        var taskEndMinutes = taskEndTimeFormatted.getMinutes();

        let startTime = addLeadingZero(taskStartHours) + ":" + addLeadingZero(taskStartMinutes);
        let endTime = addLeadingZero(taskEndHours) + ":" + addLeadingZero(taskEndMinutes);

        innerStrendDiv.className = "list__item__strend";
        innerStrendDiv.textContent = `${startTime} - ${endTime}`;

        // Вычисляем разницу времени в минутах
        var minuteDifference = getMinuteDifference(taskStartTimeFormatted, taskEndTimeFormatted);

        // Вычисляем часы и минуты из разницы времени в минутах
        var diffHours = Math.floor(minuteDifference / 60);
        var diffMinutes = minuteDifference % 60;

        // Форматируем разницу времени в строку "HH:MM"
        var formattedDifference = formatDuration(task_duration);

        innerSpendTimeDiv.className = "list__item__sepndtime";
        innerSpendTimeDiv.textContent = formattedDifference;

        innerA.appendChild(innerTitleDiv);
        innerA.appendChild(innerStrendDiv);
        innerA.appendChild(innerSpendTimeDiv);

        innerLi.appendChild(innerA);

        tasksList.appendChild(innerLi);

        innerLi.querySelector(".popup-link").addEventListener("click", function (e) {
          e.preventDefault();
          const popupName = this.getAttribute('href').replace('#', '');
          const currPopup = document.getElementById(popupName);

          if (this.hasAttribute('data-item-id')) {
            const itemId = this.getAttribute('data-item-id');
            const hiddenInput = currPopup.querySelector("[name='taskId']");
            hiddenInput.value = itemId;
            hiddenInput.dispatchEvent(new Event('change'));
          }

          popupOpen(currPopup)
        });

        sortAndGetTotalTime();

      } else {

        innerStrendDiv.className = "list__item__strend";
        innerSpendTimeDiv.className = "list__item__sepndtime";

        innerA.appendChild(innerTitleDiv);
        innerA.appendChild(innerStrendDiv);
        innerA.appendChild(innerSpendTimeDiv);

        innerLi.appendChild(innerA);

        tasksList.appendChild(innerLi);

        innerLi.querySelector(".popup-link").addEventListener("click", function (e) {
          e.preventDefault();
          const popupName = this.getAttribute('href').replace('#', '');
          const currPopup = document.getElementById(popupName);

          if (this.hasAttribute('data-item-id')) {
            const itemId = this.getAttribute('data-item-id');
            const hiddenInput = currPopup.querySelector("[name='taskId']");
            hiddenInput.value = itemId;
            hiddenInput.dispatchEvent(new Event('change'));
          }

          popupOpen(currPopup)
        });

      }

      let popupId = "add-completed-task-popup";
      let popupActive = document.getElementById(popupId);
      popupActive.querySelector("input[name='task_name']").value = "";
      popupActive.querySelector("input[name='task__start']").value = "";
      popupActive.querySelector("input[name='task__end']").value = "";
      popupClose(popupActive);
    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function editCompletedTask() {

  let form = document.getElementById("edit__completed__task__popup__form");

  let taskName = form.querySelector(".task__name").value;
  if (taskName.trim() === "") {
    alert("Введите название задачи");
    return;
  }

  let taskStart = form.querySelector(".task__start").value;
  let taskEnd = form.querySelector(".task__end").value;

  var timeFormat = /^([01]\d|2[0-3]):([0-5]\d)$/;
  if ((timeFormat.test(taskStart) && timeFormat.test(taskEnd)) || (taskStart === "" && taskEnd === "")) {
    if (taskStart === "" && taskEnd === "") {
      console.log('Правильное время');
    } else {
      // Если формат правильный, разбиваем строку на часы и минуты
      var taskStartSplit = taskStart.split(':');
      var startHours = parseInt(taskStartSplit[0], 10);
      var startMinutes = parseInt(taskStartSplit[1], 10);

      // Создаем объект времени с сегодняшней датой и введенным временем
      var startTimeObj = new Date();
      startTimeObj.setHours(startHours);
      startTimeObj.setMinutes(startMinutes);

      var taskEndSplit = taskEnd.split(':');
      var endHours = parseInt(taskEndSplit[0], 10);
      var endMinutes = parseInt(taskEndSplit[1], 10);

      // Создаем объект времени с сегодняшней датой и введенным временем
      var endTimeObj = new Date();
      endTimeObj.setHours(endHours);
      endTimeObj.setMinutes(endMinutes);

      if (startTimeObj >= endTimeObj) {
        alert('Время окончания задачи должно превышать время начала!');
        return;
      } else {
        console.log('Правильное время');
      }
    }
  } else {
    alert('Неправильный формат времени!');
    return;
  }

  // Собираем данные формы
  let formData = new FormData(form);
  formData.append('task_name', taskName);
  formData.append('task_start_time', taskStart);
  formData.append('task_end_time', taskEnd);

  // Отправляем асинхронный запрос на сервер
  fetch("/edit-completed-task/", {
    method: form.method,
    body: formData,
    headers: {
      // 'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => response.json())
    .then(data => {

      let task_id = data.task_id;
      let start_time = data.start_time;
      let end_time = data.end_time;
      let task_duration = data.task_duration;

      let tasksList = document.getElementById('today__tasks__block__list');

      console.log(start_time);
      console.log(end_time);
      console.log(task_duration);

      if (start_time !== "" && end_time !== "") {
        console.log(true);

        let listItems = tasksList.querySelectorAll(".list__item a");

        listItems.forEach(function (item) {
          // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
          console.log('1');
          console.log(task_id);
          if (item.hasAttribute('data-item-id') && item.getAttribute('data-item-id') == task_id) {
            console.log('2');
            // Добавление класса "highlight" к текущему элементу <li>
            let divTime = item.querySelector(".list__item__strend");
            divTime.textContent = `${start_time} - ${end_time}`;

            let taskDurationFormatted = formatDuration(task_duration);

            item.querySelector(".list__item__sepndtime").textContent = taskDurationFormatted;
            item.querySelector(".list__item__title").textContent = taskName;

            let popupId = item.getAttribute('href').replace('#', '');
            let popupActive = document.getElementById(popupId);

            item.closest("li").classList.add("with__time");

            popupClose(popupActive);
          }
        });

        sortAndGetTotalTime();

      } else {
        console.log(false);

        let listItems = tasksList.querySelectorAll(".list__item a");
        console.log(task_id);

        listItems.forEach(function (item) {
          // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
          if (item.hasAttribute('data-item-id') && item.getAttribute('data-item-id') == task_id) {
            // Добавление класса "highlight" к текущему элементу <li>
            let divTime = item.querySelector(".list__item__strend");
            divTime.textContent = "";

            item.querySelector(".list__item__sepndtime").textContent = "";

            let popupId = item.getAttribute('href').replace('#', '');
            let popupActive = document.getElementById(popupId);

            popupClose(popupActive);

            let li = item.closest("li");
            li.classList.remove("with__time");
            let clonedLi = li.cloneNode(true);

            clonedLi.querySelector(".list__item__title").textContent = taskName;

            li.remove();

            let ul = document.getElementById("today__tasks__block__list");
            ul.appendChild(clonedLi);

            clonedLi.querySelector(".popup-link").addEventListener("click", function (e) {
              e.preventDefault();
              const popupName = this.getAttribute('href').replace('#', '');
              const currPopup = document.getElementById(popupName);

              if (this.hasAttribute('data-item-id')) {
                const itemId = this.getAttribute('data-item-id');
                const hiddenInput = currPopup.querySelector("[name='taskId']");
                hiddenInput.value = itemId;
                hiddenInput.dispatchEvent(new Event('change'));
              }

              popupOpen(currPopup)
            });

          }
        });

      }

    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function deleteCompletedTask() {
  let form = document.getElementById("edit__completed__task__popup__form");

  // Собираем данные формы
  let formData = new FormData(form);

  // Отправляем асинхронный запрос на сервер
  fetch("/delete-completed-task/", {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => response.json())
    .then(data => {

      let task_id = data.task_id;
      let tasksList = document.getElementById('today__tasks__block__list');
      let listItems = tasksList.querySelectorAll(".tasks__block__list__item a");

      listItems.forEach(function (item) {
        // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
        if (item.hasAttribute('data-item-id') && item.getAttribute('data-item-id') == task_id) {
          // Добавление класса "highlight" к текущему элементу <li>
          let li = item.closest("li");
          let popupId = item.getAttribute('href').replace('#', '');
          let popupActive = document.getElementById(popupId);

          popupClose(popupActive);
          li.remove();
        }
      });

      sortAndGetTotalTime();

    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function deleteEditableTask() {
  let form = document.getElementById("edit__pending__popup__form");

  // Собираем данные формы
  let formData = new FormData(form);

  // Отправляем асинхронный запрос на сервер
  fetch("/remove-pending-task/", {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => response.json())
    .then(data => {

      let task_id = data.task_id;
      let tasksList = document.getElementById('upper__tasks__block__list');
      let listItems = tasksList.querySelectorAll(".tasks__block__list__item a");

      listItems.forEach(function (item) {
        // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
        if (item.hasAttribute('data-item-id') && item.getAttribute('data-item-id') == task_id) {
          // Добавление класса "highlight" к текущему элементу <li>
          let li = item.closest("li");
          let popupId = item.getAttribute('href').replace('#', '');
          let popupActive = document.getElementById(popupId);

          popupClose(popupActive);
          li.remove();
        }
      });
    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function editCredentials() {
  let form = document.getElementById("edit__credentials__popup__form");
  let login = form.querySelector(".login").value;
  let password = form.querySelector(".password").value;

  if (login.trim() === '' || password.trim() === '') {
    alert("Введите логин и пароль");
    return;
  }

  console.log("work");

  let formData = new FormData(form);
  formData.append('login', login);
  formData.append('password', password);

  fetch("/edit-credentials/", {
    method: form.method,
    body: formData,
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
    })
    .then(data => {
      window.location.pathname = "/logout/";
    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });

}

function makePendingTaskActive(e) {

  e.stopPropagation();

  let icon = e.target;
  let item_id = icon.closest("a").getAttribute("data-item-id");

  console.log(item_id);

  fetch("/make-pending-task-active/", {
    method: "POST",
    body: JSON.stringify({ item_id }),
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return response.json();
    })
    .then(data => {
      console.log('rabotaet');

      let taskId = data.task_id;
      let start = data.start;
      let taskName = data.task_name;

      let li = icon.closest("li");
      li.remove();

      let taskList = document.getElementById("upper__tasks__block__list");

      let taskLi = document.createElement("li");
      taskLi.classList.add("tasks__block__list__item", "list__item", "active__task");

      let innerA = document.createElement("a");
      innerA.href = "#";
      innerA.classList.add("list__item__link");
      innerA.setAttribute("data-item-id", taskId);

      let innerTitleDiv = document.createElement("div");
      innerTitleDiv.className = "list__item__title";
      innerTitleDiv.textContent = taskName;

      let innerStrendDiv = document.createElement("div");
      innerStrendDiv.className = "list__item__strend";
      innerStrendDiv.textContent = `${start} - ${start}`;

      let innerStrendTimeDiv = document.createElement("div");
      innerStrendTimeDiv.className = "list__item__sepndtime";

      let pElement = document.createElement("p");
      pElement.textContent = "00:00";

      let iElement = document.createElement("i");
      iElement.classList.add("_icon-stop-circle");
      iElement.setAttribute("onclick", "finishActiveTask()");

      innerStrendTimeDiv.appendChild(pElement);
      innerStrendTimeDiv.appendChild(iElement)

      innerA.appendChild(innerTitleDiv);
      innerA.appendChild(innerStrendDiv);
      innerA.appendChild(innerStrendTimeDiv);

      taskLi.appendChild(innerA);

      taskList.appendChild(taskLi);

      let firstTask = taskList.firstChild;
      if (firstTask !== null) {
        // Если есть, вставляем новый элемент перед первым элементом в списке
        taskList.insertBefore(taskLi, firstTask);
      } else {
        // Если список пуст, просто добавляем новый элемент в конец
        taskList.appendChild(taskLi);
      }

      let activeTask = document.querySelector(".active__task");
      let timerDiv = activeTask.querySelector(".list__item__sepndtime p");
      // Стартуем секундомер для новой задачи
      startTimer(timerDiv);

    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });

}

const pendingTasks = document.querySelectorAll(".waiting-task");

for (let i = 0; i < pendingTasks.length; i++) {

  pendingTasks[i].querySelector("._icon-play").addEventListener("click", makePendingTaskActive)

}

const downloadMore = document.querySelector(".download-more")
async function addTaskBlock(e) {
  const tasksContainer = document.querySelector('.tasks')
  const tasks = document.querySelectorAll('.tasks__block')
  const lastTaskName = tasks[tasks.length - 1].querySelector('.tasks__block__info__title h2').textContent.split(",")[0];
  function parseDateString(dateString) {
    const today = new Date()

    if (dateString.toLowerCase() === "сегодня") {
      return today;
    }

    const parts = dateString.split(" ");

    const day = parseInt(parts[0]);
    const month = parts[1];

    // Map month names to month numbers
    const monthsMap = {
      "января": 0, "февраля": 1, "марта": 2, "апреля": 3, "мая": 4,
      "июня": 5, "июля": 6, "августа": 7, "сентября": 8, "октября": 9,
      "ноября": 10, "декабря": 11
    };

    const monthNumber = monthsMap[month.toLowerCase()];

    // Создаем новый объект Date с указанным днем и месяцем
    const date = new Date(today.getFullYear(), monthNumber, day);
    

    return date;
  }

  function insertNewTasksBlock(data) {

  }

  const dateObj = parseDateString(lastTaskName)
  const dateUTC = new Date(Date.UTC(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate()));

  console.log(dateObj);
  console.log(dateUTC);

  try {
    const data = await fetch('/load-next-completed-tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ date: dateUTC })
    })

    console.log(data)
  } catch (e) {
    console.error("can't get previous tasks. error: ", e)
  }

}
downloadMore.addEventListener('click', addTaskBlock)