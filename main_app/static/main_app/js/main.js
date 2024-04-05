function addActiveTask() {
    // Ищем на странице активную задачу
    let activeTask = document
        .querySelector(".active__tasks")
        .querySelector("li.active__task");

    // Проверяем присутствует ли на странице активная задача
    if (activeTask) {
        let currPopup = document.getElementById(
            "finish-active-task-warning-popup"
        );
        popupOpen(currPopup);
        return;
    }

    // Собираем данные формы
    let form = document.getElementById("tasks__form");
    let formData = new FormData(form);
    let taskName = form.task_name.value;

    // Проверяем, что текст задачи не пустой
    if (isEmpty(taskName)) {
        return;
    }

    // Отправляем асинхронный запрос на сервер
    fetch("/add-active-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            // Проверяем, есть ли в БД активная задача
            let task_already_present = data.task_already_present;
            if (task_already_present) {
                let currPopup = document.getElementById(
                    "finish-active-task-warning-popup"
                );
                popupOpen(currPopup);
                return;
            }

            let taskList = document.querySelector(".tasks__block__list");
            let taskId = data.task_id;
            let start = data.start;

            let taskLi = document.createElement("li");
            taskLi.classList.add(
                "tasks__block__list__item",
                "list__item",
                "active__task"
            );

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
            innerStrendTimeDiv.className = "list__item__spendtime";

            let pElement = document.createElement("p");
            pElement.textContent = "00:00";

            let iElement = document.createElement("i");
            iElement.classList.add("_icon-stop-circle");
            iElement.setAttribute("onclick", "finishActiveTask()");

            innerStrendTimeDiv.appendChild(pElement);
            innerStrendTimeDiv.appendChild(iElement);

            innerA.appendChild(innerTitleDiv);
            innerA.appendChild(innerStrendDiv);
            innerA.appendChild(innerStrendTimeDiv);

            taskLi.appendChild(innerA);

            taskList.appendChild(taskLi);

            // Берем первый чайлд у списка активных задач
            let firstTask = taskList.firstChild;
            if (firstTask !== null) {
                // Если задачи есть, вставляем новый элемент перед первым элементом в списке
                taskList.insertBefore(taskLi, firstTask);
            } else {
                // Если задач нет, просто добавляем новый элемент в конец
                taskList.appendChild(taskLi);
            }

            let activeTask = document.querySelector(".active__task");
            let timerDiv = activeTask.querySelector(".list__item__spendtime p");

            // Стартуем секундомер для новой задачи
            startTimer(timerDiv);
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });

    form.querySelector(".input").value = "";
}

function addPendingTask() {
    // Собираем данные формы
    let form = document.getElementById("tasks__form");
    let formData = new FormData(form);
    let taskName = form.task_name.value;

    // Проверяем, что текст задачи не пустой
    if (isEmpty(taskName)) {
        return;
    }

    // Отправляем асинхронный запрос на сервер
    fetch("/add-pending-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let taskList = document.querySelector(".tasks__block__list");
            let taskId = data.task_id;

            let taskLi = document.createElement("li");
            taskLi.classList.add(
                "tasks__block__list__item",
                "list__item",
                "waiting-task"
            );

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
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });

    form.querySelector(".input").value = "";
}

function finishActiveTask() {
    // Получаем первичный ключ активной задачи
    let taskId = document
        .querySelector(".active__task a")
        .getAttribute("data-item-id");

    // Получаем значение csrf токена
    let csrfTokenInput = document
        .getElementById("tasks__form")
        .querySelector('input[name="csrfmiddlewaretoken"]');
    let csrfTokenValue = csrfTokenInput.value;

    // Получаем время активной задачи
    let timeCurrent = document.querySelector(
        ".active__task .list__item__spendtime p"
    ).textContent;
    let timeCurrentSplitted = timeCurrent.split(":");
    let minutesCurrent = timeCurrentSplitted[0].trim();
    let minutesCurrentInt = parseInt(minutesCurrent, 10);

    // Проверяем что время активной задачи не менее 1 минуты
    if (minutesCurrentInt < 1) {
        popupOpen(document.getElementById("less-than-minute-popup"));
        return;
    }

    // Отправляем асинхронный запрос на сервер
    fetch("/finish-active-task/", {
        method: "POST",
        body: JSON.stringify({ taskId }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfTokenValue,
        },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let taskDuration = data.task_duration;
            let activeTask = document.querySelector(".active__task");
            let clonedElement = activeTask.cloneNode(true);
            activeTask.remove();
            clonedElement.classList.remove("active__task");
            clonedElement.classList.add("done", "with__time");
            clonedElement
                .querySelector("a")
                .setAttribute("href", "#edit-completed-task-popup");
            clonedElement.querySelector("a").classList.add("popup-link");

            clonedElement.querySelector(".list__item__spendtime").textContent =
                formatDuration(taskDuration);

            let ul = document.getElementById("today__tasks__block__list");
            ul.appendChild(clonedElement);

            sortAndGetTotalTime();

            clonedElement
                .querySelector(".popup-link")
                .addEventListener("click", function (e) {
                    e.preventDefault();
                    const popupName = this.getAttribute("href").replace(
                        "#",
                        ""
                    );
                    const currPopup = document.getElementById(popupName);

                    if (this.hasAttribute("data-item-id")) {
                        const itemId = this.getAttribute("data-item-id");
                        const hiddenInput =
                            currPopup.querySelector("[name='task_id']");
                        hiddenInput.value = itemId;
                        hiddenInput.dispatchEvent(new Event("change"));
                    }

                    popupOpen(currPopup);
                });
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function editPendingTask() {
    // Собираем данные формы
    let form = document.getElementById("edit__pending__popup__form");
    let formData = new FormData(form);
    let taskName = form.task_name.value;

    // Проверяем, что текст задачи не пустой
    if (isEmpty(taskName)) {
        return;
    }

    // Отправляем асинхронный запрос на сервер
    fetch("/edit-pending-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let taskId = data.task_id;
            let tasksList = document.getElementById(
                "upper__tasks__block__list"
            );
            let listItems = tasksList.querySelectorAll(
                ".tasks__block__list__item a"
            );

            listItems.forEach(function (item) {
                // Проверка наличия атрибута "data-item-id" и сравнение его значения с необходимым
                if (
                    item.hasAttribute("data-item-id") &&
                    item.getAttribute("data-item-id") == taskId
                ) {
                    let divTitle = item.querySelector(".list__item__title");
                    divTitle.textContent = taskName;

                    let popupId = item.getAttribute("href").replace("#", "");
                    let popupActive = document.getElementById(popupId);
                    popupActive.querySelector("input[name='task_name']").value =
                        "";
                    popupClose(popupActive);
                }
            });
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function removePendingTask() {
    // Собираем данные формы
    let form = document.getElementById("edit__pending__popup__form");
    let formData = new FormData(form);

    // Отправляем асинхронный запрос на сервер
    fetch("/remove-pending-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let taskId = data.task_id;
            let tasksList = document.getElementById(
                "upper__tasks__block__list"
            );
            let listItems = tasksList.querySelectorAll(
                ".tasks__block__list__item a"
            );

            listItems.forEach(function (item) {
                // Проверка наличия атрибута "data-item-id" и сравнение его значения с необходимым
                if (
                    item.hasAttribute("data-item-id") &&
                    item.getAttribute("data-item-id") == taskId
                ) {
                    let li = item.closest("li");
                    let popupId = item.getAttribute("href").replace("#", "");
                    let popupActive = document.getElementById(popupId);

                    popupClose(popupActive);
                    li.remove();
                }
            });
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function addCompletedTask() {
    // Собираем данные формы
    let form = document.getElementById("add__completed__task__popup__form");
    let formData = new FormData(form);
    let taskName = form.task_name.value;
    let taskStart = form.task_start.value;
    let taskEnd = form.task_end.value;

    // Проверяем, что текст задачи не пустой
    if (isEmpty(taskName)) {
        return;
    }

    // Проверяем корректность времени
    if (!isTimeCorrect(taskStart, taskEnd)) {
        return;
    }

    // Отправляем асинхронный запрос на сервер
    fetch("/add-completed-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let taskId = data.task_id;
            let taskStartTime = data.task_start_time;
            let taskEndTime = data.task_end_time;
            let task_duration = data.task_duration;

            let tasksList = document.getElementById(
                "today__tasks__block__list"
            );

            let innerLi = document.createElement("li");
            innerLi.classList.add(
                "tasks__block__list__item",
                "list__item",
                "done"
            );

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
                console.log("not null");

                innerLi.classList.add("with__time");

                function addLeadingZero(num) {
                    return (num < 10 ? "0" : "") + num;
                }

                var taskStartTimeFormatted = new Date(taskStartTime);
                var taskEndTimeFormatted = new Date(taskEndTime);

                var taskStartHours = taskStartTimeFormatted.getHours();
                var taskStartMinutes = taskStartTimeFormatted.getMinutes();

                var taskEndHours = taskEndTimeFormatted.getHours();
                var taskEndMinutes = taskEndTimeFormatted.getMinutes();

                let startTime =
                    addLeadingZero(taskStartHours) +
                    ":" +
                    addLeadingZero(taskStartMinutes);
                let endTime =
                    addLeadingZero(taskEndHours) +
                    ":" +
                    addLeadingZero(taskEndMinutes);

                innerStrendDiv.className = "list__item__strend";
                innerStrendDiv.textContent = `${startTime} - ${endTime}`;

                // Вычисляем разницу времени в минутах
                var minuteDifference = getMinuteDifference(
                    taskStartTimeFormatted,
                    taskEndTimeFormatted
                );

                // Вычисляем часы и минуты из разницы времени в минутах
                var diffHours = Math.floor(minuteDifference / 60);
                var diffMinutes = minuteDifference % 60;

                // Форматируем разницу времени в строку "HH:MM"
                var formattedDifference = formatDuration(task_duration);

                innerSpendTimeDiv.className = "list__item__spendtime";
                innerSpendTimeDiv.textContent = formattedDifference;

                innerA.appendChild(innerTitleDiv);
                innerA.appendChild(innerStrendDiv);
                innerA.appendChild(innerSpendTimeDiv);

                innerLi.appendChild(innerA);

                tasksList.appendChild(innerLi);

                innerLi
                    .querySelector(".popup-link")
                    .addEventListener("click", function (e) {
                        e.preventDefault();
                        const popupName = this.getAttribute("href").replace(
                            "#",
                            ""
                        );
                        const currPopup = document.getElementById(popupName);

                        if (this.hasAttribute("data-item-id")) {
                            const itemId = this.getAttribute("data-item-id");
                            const hiddenInput =
                                currPopup.querySelector("[name='task_id']");
                            hiddenInput.value = itemId;
                            hiddenInput.dispatchEvent(new Event("change"));
                        }

                        popupOpen(currPopup);
                    });

                sortAndGetTotalTime();
            } else {
                innerStrendDiv.className = "list__item__strend";
                innerSpendTimeDiv.className = "list__item__spendtime";

                innerA.appendChild(innerTitleDiv);
                innerA.appendChild(innerStrendDiv);
                innerA.appendChild(innerSpendTimeDiv);

                innerLi.appendChild(innerA);

                tasksList.appendChild(innerLi);

                innerLi
                    .querySelector(".popup-link")
                    .addEventListener("click", function (e) {
                        e.preventDefault();
                        const popupName = this.getAttribute("href").replace(
                            "#",
                            ""
                        );
                        const currPopup = document.getElementById(popupName);

                        if (this.hasAttribute("data-item-id")) {
                            const itemId = this.getAttribute("data-item-id");
                            const hiddenInput =
                                currPopup.querySelector("[name='task_id']");
                            hiddenInput.value = itemId;
                            hiddenInput.dispatchEvent(new Event("change"));
                        }

                        popupOpen(currPopup);
                    });
            }

            let popupId = "add-completed-task-popup";
            let popupActive = document.getElementById(popupId);
            popupActive.querySelector("input[name='task_name']").value = "";
            popupActive.querySelector("input[name='task_start']").value = "";
            popupActive.querySelector("input[name='task_end']").value = "";
            popupClose(popupActive);
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function editCompletedTask() {
    // Собираем данные формы
    let form = document.getElementById("edit__completed__task__popup__form");
    let formData = new FormData(form);
    let taskName = form.task_name.value;
    let taskStart = form.task_start.value;
    let taskEnd = form.task_end.value;

    // Проверяем, что текст задачи не пустой
    if (isEmpty(taskName)) {
        return;
    }

    // Проверяем корректность времени
    if (!isTimeCorrect(taskStart, taskEnd)) {
        return;
    }

    // Отправляем асинхронный запрос на сервер
    fetch("/edit-completed-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let task_id = data.task_id;
            let start_time = data.start_time;
            let end_time = data.end_time;
            let task_duration = data.task_duration;

            let tasksList = document.getElementById(
                "today__tasks__block__list"
            );

            console.log(start_time);
            console.log(end_time);
            console.log(task_duration);

            if (start_time !== "" && end_time !== "") {
                console.log(true);

                let listItems = tasksList.querySelectorAll(".list__item a");

                listItems.forEach(function (item) {
                    // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
                    console.log("1");
                    console.log(task_id);
                    if (
                        item.hasAttribute("data-item-id") &&
                        item.getAttribute("data-item-id") == task_id
                    ) {
                        console.log("2");
                        // Добавление класса "highlight" к текущему элементу <li>
                        let divTime = item.querySelector(".list__item__strend");
                        divTime.textContent = `${start_time} - ${end_time}`;

                        let taskDurationFormatted =
                            formatDuration(task_duration);

                        item.querySelector(
                            ".list__item__spendtime"
                        ).textContent = taskDurationFormatted;
                        item.querySelector(".list__item__title").textContent =
                            taskName;

                        let popupId = item
                            .getAttribute("href")
                            .replace("#", "");
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
                    if (
                        item.hasAttribute("data-item-id") &&
                        item.getAttribute("data-item-id") == task_id
                    ) {
                        // Добавление класса "highlight" к текущему элементу <li>
                        let divTime = item.querySelector(".list__item__strend");
                        divTime.textContent = "";

                        item.querySelector(
                            ".list__item__spendtime"
                        ).textContent = "";

                        let popupId = item
                            .getAttribute("href")
                            .replace("#", "");
                        let popupActive = document.getElementById(popupId);

                        popupClose(popupActive);

                        let li = item.closest("li");
                        li.classList.remove("with__time");
                        let clonedLi = li.cloneNode(true);

                        clonedLi.querySelector(
                            ".list__item__title"
                        ).textContent = taskName;

                        li.remove();

                        let ul = document.getElementById(
                            "today__tasks__block__list"
                        );
                        ul.appendChild(clonedLi);

                        clonedLi
                            .querySelector(".popup-link")
                            .addEventListener("click", function (e) {
                                e.preventDefault();
                                const popupName = this.getAttribute(
                                    "href"
                                ).replace("#", "");
                                const currPopup =
                                    document.getElementById(popupName);

                                if (this.hasAttribute("data-item-id")) {
                                    const itemId =
                                        this.getAttribute("data-item-id");
                                    const hiddenInput =
                                        currPopup.querySelector(
                                            "[name='task_id']"
                                        );
                                    hiddenInput.value = itemId;
                                    hiddenInput.dispatchEvent(
                                        new Event("change")
                                    );
                                }

                                popupOpen(currPopup);
                            });
                    }
                });
            }
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function deleteCompletedTask() {
    // Собираем данные формы
    let form = document.getElementById("edit__completed__task__popup__form");
    let formData = new FormData(form);

    // Отправляем асинхронный запрос на сервер
    fetch("/delete-completed-task/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let task_id = data.task_id;
            let tasksList = document.getElementById(
                "today__tasks__block__list"
            );
            let listItems = tasksList.querySelectorAll(
                ".tasks__block__list__item a"
            );

            listItems.forEach(function (item) {
                // Проверка наличия атрибута "data-item-id" и сравнение его значения с желаемым
                if (
                    item.hasAttribute("data-item-id") &&
                    item.getAttribute("data-item-id") == task_id
                ) {
                    // Добавление класса "highlight" к текущему элементу <li>
                    let li = item.closest("li");
                    let popupId = item.getAttribute("href").replace("#", "");
                    let popupActive = document.getElementById(popupId);

                    popupClose(popupActive);
                    li.remove();
                }
            });

            sortAndGetTotalTime();
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function makePendingTaskActive(e) {
    // Предотвращаем появление попапа с редактированием задачи
    e.stopPropagation();

    // Получаем id задачи
    let icon = e.target;
    let itemId = icon.closest("a").getAttribute("data-item-id");

    // Получаем из cookie значение csrftoken
    const csrftoken = getCookie("csrftoken");

    fetch("/make-pending-task-active/", {
        method: "POST",
        body: JSON.stringify({ itemId }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            let taskId = data.task_id;
            let start = data.start;
            let taskName = data.task_name;

            let li = icon.closest("li");
            li.remove();

            let taskList = document.getElementById("upper__tasks__block__list");

            let taskLi = document.createElement("li");
            taskLi.classList.add(
                "tasks__block__list__item",
                "list__item",
                "active__task"
            );

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
            innerStrendTimeDiv.className = "list__item__spendtime";

            let pElement = document.createElement("p");
            pElement.textContent = "00:00";

            let iElement = document.createElement("i");
            iElement.classList.add("_icon-stop-circle");
            iElement.setAttribute("onclick", "finishActiveTask()");

            innerStrendTimeDiv.appendChild(pElement);
            innerStrendTimeDiv.appendChild(iElement);

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
            let timerDiv = activeTask.querySelector(".list__item__spendtime p");
            // Стартуем секундомер для новой задачи
            startTimer(timerDiv);
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function editCredentials() {
    // Собираем данные формы
    let form = document.getElementById("edit__credentials__popup__form");
    let formData = new FormData(form);
    let username = form.username.value;
    let newPassword1 = form.new_password1.value;
    let newPassword2 = form.new_password2.value;

    // Проверяем, что логин и пароли не пустые
    if (!username && !newPassword1 && !newPassword2) {
        return;
    }

    fetch("/edit-credentials/", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            if (data.success) {
                window.location.pathname = "/login/";
            } else {
                // Ищем все теги ul в форме
                let ulElements = form.getElementsByTagName("ul");

                // Проходимся по всем найденным элементам ul и удаляем их
                while (ulElements.length > 0) {
                    ulElements[0].parentNode.removeChild(ulElements[0]);
                    ulElements = form.getElementsByTagName("ul");
                }

                // Проходимся по каждой ошибке
                for (const field in data.errors) {
                    // Проверяем, что сообщение об ошибке не пустое
                    if (data.errors[field] !== " ") {
                        let inputElement = form.querySelector(
                            `input[name="${field}"]`
                        );
                        if (inputElement) {
                            inputElement.classList.add("error");
                        }

                        let ulErrorBlock = document.createElement("ul");
                        ulErrorBlock.className = "profile__edit__errors";

                        let divErrorBlock = document.createElement("div");
                        divErrorBlock.id = field + "__error";
                        divErrorBlock.innerText = data.errors[field];

                        ulErrorBlock.appendChild(divErrorBlock);

                        // Добавляем блок с ошибкой после соответствующего div
                        inputElement.parentNode.insertAdjacentElement(
                            "afterend",
                            ulErrorBlock
                        );
                    }
                }
            }
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

function loadNextCompletedTasks() {
    let tasksBlock = document.querySelectorAll(".tasks__block");
    let lastTaskBlockDate = tasksBlock[tasksBlock.length - 1]
        .querySelector(".tasks__block__info__title h2")
        .textContent.split(",")[0];

    // Получаем дату для отправки на сервер
    let dateToSend = getDateToSend(lastTaskBlockDate);

    // Получаем из cookie значение csrftoken
    const csrftoken = getCookie("csrftoken");

    // Отправляем асинхронный запрос на сервер
    fetch("/load-next-completed-tasks/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ date: dateToSend }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Ошибка сети");
            }
            return response.json();
        })
        .then((data) => {
            // Проверяем, если задачи закончились
            if (data.success && data.is_end_of_tasks) {
                let endOfTasksPopup = document.getElementById(
                    "end-of-tasks-warning-popup"
                );
                popupOpen(endOfTasksPopup);

                let loadMoreButton = document.querySelector(
                    ".footer__options__item.download-more a"
                );
                if (loadMoreButton) {
                    loadMoreButton.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                    });
                }

                return;
            }

            if (
                !data.completed_tasks_with_time.length &&
                !data.completed_tasks_no_time.length
            ) {
                return;
            }

            let tasksDiv = document.querySelector(".tasks");

            let tasksBlock = document.createElement("div");
            tasksBlock.classList.add("tasks__block");

            let blockInfo = document.createElement("div");
            blockInfo.classList.add("tasks__block__info");

            let blockTitle = document.createElement("div");
            blockTitle.classList.add("tasks__block__info__title");

            let titleHeading = document.createElement("h2");
            titleHeading.textContent = data.title_date;

            let blockTime = document.createElement("div");
            blockTime.classList.add("tasks__block__info__time");
            if (data.completed_tasks_total_time !== "0 м") {
                blockTime.textContent = data.completed_tasks_total_time;
            }

            let blockList = document.createElement("ul");
            blockList.classList.add("tasks__block__list", "disable-hover");

            data.completed_tasks_with_time.forEach((task) => {
                let listItem = document.createElement("li");
                listItem.classList.add(
                    "tasks__block__list__item",
                    "list__item",
                    "done"
                );

                let listItemLink = document.createElement("a");
                listItemLink.href = "#";
                listItemLink.classList.add("list__item__link");

                let titleDiv = document.createElement("div");
                titleDiv.classList.add("list__item__title");
                titleDiv.textContent = task.task_name;

                let strendDiv = document.createElement("div");
                strendDiv.classList.add("list__item__strend");
                strendDiv.textContent =
                    task.completed_task_start_time +
                    " - " +
                    task.completed_task_end_time;

                let spendtimeDiv = document.createElement("div");
                spendtimeDiv.classList.add("list__item__spendtime");
                spendtimeDiv.textContent = task.completed_task_time_difference;

                listItemLink.appendChild(titleDiv);
                listItemLink.appendChild(strendDiv);
                listItemLink.appendChild(spendtimeDiv);
                listItem.appendChild(listItemLink);
                blockList.appendChild(listItem);
            });

            data.completed_tasks_no_time.forEach((task) => {
                let listItem = document.createElement("li");
                listItem.classList.add(
                    "tasks__block__list__item",
                    "list__item",
                    "done"
                );

                let listItemLink = document.createElement("a");
                listItemLink.href = "#";
                listItemLink.classList.add("list__item__link");

                let titleDiv = document.createElement("div");
                titleDiv.classList.add("list__item__title");
                titleDiv.textContent = task.task_name;

                let strendDiv = document.createElement("div");
                strendDiv.classList.add("list__item__strend");
                strendDiv.textContent = "";

                let spendtimeDiv = document.createElement("div");
                spendtimeDiv.classList.add("list__item__spendtime");
                spendtimeDiv.textContent = "";

                listItemLink.appendChild(titleDiv);
                listItemLink.appendChild(strendDiv);
                listItemLink.appendChild(spendtimeDiv);
                listItem.appendChild(listItemLink);
                blockList.appendChild(listItem);
            });

            tasksBlock.appendChild(blockInfo);
            blockInfo.appendChild(blockTitle);
            blockTitle.appendChild(titleHeading);
            blockInfo.appendChild(blockTime);
            tasksBlock.appendChild(blockList);
            tasksDiv.append(tasksBlock);

            let loadMoreButton = document.querySelector(
                ".footer__options__item.download-more a"
            );
            if (loadMoreButton) {
                loadMoreButton.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            }
        })
        .catch((error) => {
            console.error("Произошла ошибка:", error);
        });
}

const downloadMore = document.querySelector(".download-more");
downloadMore.addEventListener("click", loadNextCompletedTasks);
