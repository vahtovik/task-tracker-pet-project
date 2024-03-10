let timers = {};
let timerStatus = {};

function addTask() {
  let form = document.getElementById("taskForm");
  let taskName = form.querySelector("#id_task").value;

  if (taskName.trim() === "") {
    alert("Введите название задачи");
    return;
  }

  // Собираем данные формы
  let formData = new FormData(form);

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
      let taskList = document.getElementById("taskList");

      let hr = document.createElement("hr");
      taskList.appendChild(hr);

      let taskId = (taskList.children.length + 1) / 2;

      let taskDiv = document.createElement("div");
      taskDiv.className = "task";
      taskDiv.id = "task" + taskId;

      let taskNameSpan = document.createElement("span");
      taskNameSpan.className = "taskName";
      taskNameSpan.textContent = taskName;
      taskNameSpan.onclick = function () { toggleTimer(taskId) };
      taskDiv.appendChild(taskNameSpan);

      let timerDiv = document.createElement("div");
      timerDiv.className = "timer";
      timerDiv.id = "timer" + taskId;
      timerDiv.textContent = "00:00";
      taskDiv.appendChild(timerDiv);

      taskList.appendChild(taskDiv);

      // Стартуем секундомер для новой задачи
      startTimer(taskId);
    })
    .catch(error => {
      console.error('Произошла ошибка:', error);
    });
}

function toggleTimer(taskId) {
  if (timers[taskId]) {
    clearInterval(timers[taskId]);
    delete timers[taskId];
    let timerDiv = document.getElementById("timer" + taskId);
    let timeParts = timerDiv.textContent.split(":");
    let minutes = parseInt(timeParts[0]);
    let seconds = parseInt(timeParts[1]);
    let totalSeconds = minutes * 60 + seconds;
    if (totalSeconds < 60) {
      alert("Задачи длительностью менее 1 минуты не сохраняются!");
      let taskDiv = document.getElementById("task" + taskId);
      let hrElement = taskDiv.previousElementSibling;
      taskDiv.parentNode.removeChild(taskDiv); // Удаление элемента div из taskList
      hrElement.parentNode.removeChild(hrElement); // Удаляем предыдущий hr
    }
    timerStatus[taskId] = false;
  } else {
    if (timerStatus[taskId] !== false) {
      startTimer(taskId);
      timerStatus[taskId] = true;
    }
  }
}

function startTimer(taskId) {
  if (!timers[taskId]) {
    timers[taskId] = setInterval(function () { incrementTimer(taskId); }, 1000);
  }
}

function incrementTimer(taskId) {
  let timerDiv = document.getElementById("timer" + taskId);
  let timeParts = timerDiv.textContent.split(":");
  let minutes = parseInt(timeParts[0]);
  let seconds = parseInt(timeParts[1]);

  seconds++;
  if (seconds >= 60) {
    seconds = 0;
    minutes++;
  }

  timerDiv.textContent = (minutes < 10 ? "0" + minutes : minutes) + ":" +
    (seconds < 10 ? "0" + seconds : seconds);
}
