fillDropdown = ->
    $.getJSON '/getnames', (data) ->
        $('#names1, #names2').each ->
            drop = $(this)
            drop.html ''
            for file in data
                drop.append $('<option/>').val(file).text(file)


fillDropdown()

String.prototype.format = String.prototype.f = ->
    s = this
    i = arguments.length

    while i--
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i])
    s

# -----------------------------------------

loadGame = (cont, history) ->
    currentTurn = 0
    blockTypes = 'red blue obstacle normal'.split ' '

    getBlock = (loc) ->
        cont.find('#p_' + loc[0] + '_' + loc[1])

    locOccupied = (loc, robots) ->
        for r in robots
            if r.location == loc
                return true
        false

    drawSingleBlock = (loc, newType) ->
        block = getBlock loc
        for t in blockTypes
            block.removeClass t
        block.addClass newType

    drawHp = (loc, hp) ->
        (getBlock loc).text hp

    drawBlocks = (oldRobots, newRobots) ->
        for robot in oldRobots
            if not locOccupied robot.location, newRobots
                drawSingleBlock robot.location, 'normal'
                drawHp robot.location, ''

        for robot in newRobots
            drawSingleBlock robot.location,
                (if robot.player_id == 0 then 'red' else 'blue')
            drawHp robot.location, robot.hp

    drawScores = (robots) ->
        score1 = 0
        score2 = 0
        for r in robots
            if r.player_id == 0 then score1++ else score2++

        cont.find('.score1').text score1
        cont.find('.score2').text score2

    drawTurn = (turn) ->
        cont.find('.turn').text turn

    loadTurn = (turn) ->
        drawBlocks history[currentTurn], history[turn]
        drawScores history[turn]
        drawTurn turn + 1
        cont.find('.block.highlighted').removeClass 'highlighted'
        displayRobotInfo false
        currentTurn = turn

    incTurn = (amt) ->
        if 0 <= currentTurn + amt < history.length
            loadTurn currentTurn + amt
            return true
        false
        
    playing = false
    timerId = 0

    play = ->
        timerId = window.setInterval (->
            if not incTurn 1
                stopTimer()
        ), 200
        playing = true
        cont.find('.btn-play').html '<i class="fa fa-stop"></i>'

    stop = ->
        window.clearInterval timerId
        playing = false
        cont.find('.btn-play').html '<i class="fa fa-play"></i>'

    cont.find('.btn-play').click    -> (if playing then stop else play)()
    cont.find('.btn-prev').click    -> incTurn -1
    cont.find('.btn-next').click    -> incTurn 1
    cont.find('.btn-rewind').click  -> loadTurn 0

    displayRobotKeyValue = (disp, k, v) ->
        disp.append($('<li/>').append($('<b/>').text(k)).append(v))

    findNextAction = (robotId) ->
        if currentTurn + 1 < history.length
            for r in history[currentTurn + 1]
                if r.robot_id == robotId
                    return r.action
        false

    formatAction = (action) ->
        if action[0] in ['move', 'attack']
            return '[\'{0}\', ({1}, {2})]'.f(action[0], action[1][0], action[1][1])
        '[\'{0}\']'.f(action[0])

    displayRobotInfo = (robot) ->
        display = cont.find('.robot-info')
        display.empty()

        if robot
            displayRobotKeyValue display, 'HP', robot.hp
            displayRobotKeyValue display, 'Location', '({0}, {1})'.f(robot.location[0], robot.location[1])
            if 'action' of robot
                displayRobotKeyValue display, 'Last action', (formatAction robot.action)

            nextAction = findNextAction robot.robot_id
            if nextAction
                displayRobotKeyValue display, 'Next action', (formatAction nextAction)
        else
            display.append($('<li/>').text('Click a robot to view its info...'))

    findRobot = (loc) ->
        for r in history[currentTurn]
            if r.location[0] == loc[0] and r.location[1] == loc[1]
                return r
        false

    idToLocation = (id) ->
        [x, y] = id.split('_')[1..2]
        [(parseInt x), (parseInt y)]

    cont.find('.block').click ->
        cont.find('.block.highlighted').removeClass 'highlighted'
        loc = idToLocation $(this).attr('id')
        robot = findRobot loc
        if robot
            $(this).addClass 'highlighted'
            (displayRobotInfo robot)
        else
            (displayRobotInfo false)

    clearBoard = ->
        cont.find('.block.red').removeClass('red').text('')
        cont.find('.block.blue').removeClass('blue').text('')

    clearBoard()
    loadTurn 0

$('#run-single').click ->
    name1 = $('#names1').val()
    name2 = $('#names2').val()
    $('#status').html 'running&hellip;'

    displayOutput = (cont, output) ->
        output = output.replace /\\n/g, '\n'
        cont.find('.output-content').html output

    displayScores = (cont, scores) ->
        if scores[0] > scores[1]
            format = '<b class="red">{0} (P1)</b> beat <b class="blue">{1} (P2)</b> {2}&ndash;{3}'
        else if scores[0] < scores[1]
            format = '<b class="blue">{1} (P2)</b> beat <b class="red">{0} (P1)</b> {3}&ndash;{2}'
        else
            format = '<span class="red">{0} (P1)</span> drew with <span class="blue">{1} (P2)</span> {2}&ndash;{3}'
        cont.find('.score').html(format.f name1, name2, scores[0], scores[1])

    displayNames = (cont) ->
        cont.find('.name1').text(name1)
        cont.find('.name2').text(name2)

    url = '/run/' + name1 + '/' + name2 + '/1'
    $.getJSON url, (data) ->
        if 'error' of data
            $('#status').html('<span class="red">' + data.error + '</span>')
            return

        $('#status').html ''
        cont = $('#container')

        displayScores cont, data.scores
        displayOutput cont, data.output
        displayNames cont
        
        output = $('#output')
        output.html cont.clone().removeClass('invis')[0].outerHTML
        loadGame output.find('.container'), data.history

$('#run-ab-test').click ->
    name1 = $('#names1').val()
    name2 = $('#names2').val()
    $('#status').html 'running&hellip;'

    displayScores = (cont, all_scores) ->
        COLUMNS = 10

        [wins1, wins2, draws] = [0, 0, 0]
        output = ''
        counter = 1

        for scores in all_scores
            if scores[0] > scores[1]
                wins1++
            else if scores[0] < scores[1]
                wins2++
            else
                draws++

            output += '{0}-{1}\t'.f(scores[0], scores[1])

            if counter % COLUMNS == 0
                output += '\n'
            counter++
        output += (if counter % COLUMNS == 1 then '\n' else '\n\n')
        output += 'Overall: {0}-{1}; {2} draws'.f(wins1, wins2, draws)
        cont.find('.output').text output

    url = '/run/' + name1 + '/' + name2 + '/100'
    $.getJSON url, (data) ->
        if 'error' of data
            $('#status').html('<span class="red">' + data.error + '</span>')
            return

        $('#status').html ''
        cont = $('#ab-container')

        displayScores cont, data
        
        output = $('#output')
        output.html cont.clone().removeClass('invis')[0].outerHTML
