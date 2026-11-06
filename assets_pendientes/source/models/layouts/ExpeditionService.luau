local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local Config=require(RS.Shared.Config.ExpeditionConfig)
local Zones=require(RS.Shared.Config.ZoneConfig)
local Notifier=require(game.ServerScriptService.Modules.Notifier)
local Builder=require(script.WorldBuilder)
local Service={Priority=56}
local records={}local uidWorld={}local rallyAt={}
local function now()return workspace:GetServerTimeNow()end
local function aliveRoot(player)
 local c=player.Character local h=c and c:FindFirstChildOfClass("Humanoid")
 return h and h.Health>0 and c:FindFirstChild("HumanoidRootPart")or nil
end
function Service:InWorld(player,id)
 local root=aliveRoot(player)
 return root~=nil and root.Position.Y>-15 and root.Position.Y<150 and Zones.Contains(id,root.Position)
end
function Service:Publish(r)
 local folder=r.State
 local boss=r.BossUid and self.Services.DestructionService:GetEntry(r.BossUid)
 local count=0 for _,p in Players:GetPlayers()do if self:InWorld(p,r.Def.Id)then count+=1 end end
 local objective
 if r.Phase=="Ready"then objective="EXPLORE OR LAUNCH AN ENCOUNTER"
 elseif r.Phase=="Shield"then objective=r.Def.Mechanic=="Beacons"and "HOLD E / TAP THE THREE BEACONS"or "BREAK THE POWER NODES"
 elseif r.Phase=="Active"then objective=r.Def.Mechanic=="Coolant"and "CORE OPEN · STRIKE BEFORE IT CLOSES"or "CORE OPEN · HIT THE BOSS, WATCH THE FLOOR"
 else objective="BOSS DEFEATED · YOUR CONTRIBUTION COUNTS"end
 for k,v in pairs({Phase=r.Phase,Objective=objective,Nodes=r.NodesDone,Goal=r.Def.Nodes,Health=boss and boss.Health or 0,MaxHealth=boss and boss.MaxHealth or 1,ReadyAt=r.ReadyAt,WindowEnds=r.WindowEnds or 0,Players=count,AttackAt=r.AttackAt or 0,AttackKind=r.AttackKind or "",AttackAxis=r.AttackAxis or 0,Enraged=r.Enraged==true})do folder:SetAttribute(k,v)end
 local world=self.WorldFolder:FindFirstChild(r.Def.Id)
 local display=world and world:FindFirstChild("EncounterBoard")and world.EncounterBoard:FindFirstChild("Display")
 if display then
  display.Heading.Text=r.Def.BossName
  display.Detail.Text=objective.."\n"..(r.Phase=="Shield"and (r.NodesDone.." / "..r.Def.Nodes.." · ")or "")..count.." EXPLORERS · ALL TOOLS CAN HELP"
 end
end
function Service:GetRecord(id)return records[id]end
function Service:Contribute(player,r)
 if not self.Data:IsLoaded(player)or not self:InWorld(player,r.Def.Id)then return end
 local item=r.Contributors[player.UserId]or {Actions=0,Last=0}
 item.Actions+=1 item.Last=now()r.Contributors[player.UserId]=item
end
function Service:RemoveTargets(r)
 local X=self.Services.DestructionService
 for uid in pairs(r.Targets)do uidWorld[uid]=nil X:Despawn(uid)end
 table.clear(r.Targets)r.BossUid=nil
 r.WindowEnds=0
 local world=self.WorldFolder and self.WorldFolder:FindFirstChild(r.Def.Id)
 if world then for _,p in world:GetDescendants()do if p:IsA("ProximityPrompt")and p:GetAttribute("ExpeditionAction")=="Beacon"then p.Enabled=false end end end
end
function Service:MakeNodes(r)
 r.Phase="Shield"r.NodesDone=0 r.Beacons={}r.WindowEnds=0 r.AttackAt=0 r.AttackKind=""
 local X=self.Services.DestructionService local boss=X:GetEntry(r.BossUid)
 if boss then boss.Invulnerable=true boss.Model:SetAttribute("Invulnerable",true)end
 for uid,kind in pairs(r.Targets)do if kind=="Node"then uidWorld[uid]=nil r.Targets[uid]=nil X:Despawn(uid)end end
 for i=1,r.Def.Nodes do
  if r.Def.Node then
   local pos=Config.NodePosition(r.Def,i)
   local uid=X:Spawn(r.Def.Node,CFrame.new(pos.X,1,pos.Z),{Zone=r.Def.Id,MaxHealth=300,Reward=0,ScrapReward=0,Xp=0,ExpeditionId=r.Def.Id,MinHit=60,MaxHit=105})
   if uid then r.Targets[uid]="Node"uidWorld[uid]=r.Def.Id end
  end
 end
 local beacons=self.WorldFolder[r.Def.Id].Beacons
 for _,b in beacons:GetDescendants()do if b:IsA("ProximityPrompt")then b.Enabled=r.Def.Mechanic=="Beacons"end end
 self:Publish(r)
end
function Service:OpenCore(r)
 if r.Phase~="Shield"then return false end
 r.Phase="Active"r.NextAttack=now()+4
 r.WindowEnds=r.Def.Window and now()+r.Def.Window or 0
 local boss=self.Services.DestructionService:GetEntry(r.BossUid)
 if boss then boss.Invulnerable=false boss.Model:SetAttribute("Invulnerable",false)end
 self:Publish(r)return true
end
function Service:StartEncounter(player,id)
 local r=records[id]
 if not r or not self:InWorld(player,id)or not self.Data:IsLoaded(player)then return false end
 if r.Phase~="Ready"and r.Phase~="Complete"then Notifier.Error(player,"THIS ENCOUNTER IS ALREADY RUNNING")return false end
 if now()<r.ReadyAt then Notifier.Error(player,"EXPLORE WHILE THE ARENA RECOVERS")return false end
 self:RemoveTargets(r)
 r.Generation+=1 r.Contributors={}r.Rewarded={}r.Enraged=false r.LastOccupied=now()r.AttackAt=0 r.AttackKind=""
 local crowd=0 for _,p in Players:GetPlayers()do if self:InWorld(p,id)then crowd+=1 end end
 local health=r.Def.Health*(1+.6*(math.clamp(crowd,1,8)-1))
 local uid=self.Services.DestructionService:Spawn(r.Def.Boss,CFrame.new(Config.BossPosition(r.Def))*CFrame.Angles(0,math.pi,0),{Zone=id,MaxHealth=health,Reward=0,ScrapReward=0,Xp=0,ExpeditionId=id,MinHit=r.Def.Health*.015,MaxHit=r.Def.Health*.035})
 if not uid then r.Phase="Ready"return false end
 r.BossUid=uid r.Targets[uid]="Boss"uidWorld[uid]=id
 self:MakeNodes(r)
 return true
end
function Service:ActivateBeacon(player,id,index)
 local r=records[id]
 if not r or r.Phase~="Shield"or r.Def.Mechanic~="Beacons"or type(index)~="number"or index%1~=0 or index<1 or index>r.Def.Nodes or r.Beacons[index]then return false end
 local root=aliveRoot(player)
 if not root or not self:InWorld(player,id)or (root.Position-Config.NodePosition(r.Def,index)).Magnitude>16 then return false end
 r.Beacons[index]=true r.NodesDone+=1 self:Contribute(player,r)
 local base=self.WorldFolder[id].Beacons:FindFirstChild("Beacon"..index)
 local prompt=base and base:FindFirstChildOfClass("ProximityPrompt")if prompt then prompt.Enabled=false end
 if r.NodesDone>=r.Def.Nodes then self:OpenCore(r)else self:Publish(r)end
 return true
end
function Service:OnWreck(entry,credits)
 local id=uidWorld[entry.Uid]local r=id and records[id]
 if not r then return end
 local kind=r.Targets[entry.Uid]uidWorld[entry.Uid]=nil r.Targets[entry.Uid]=nil
 if kind=="Node"and r.Phase=="Shield"then
  r.NodesDone+=1
  if r.NodesDone>=r.Def.Nodes then self:OpenCore(r)else self:Publish(r)end
 elseif kind=="Boss"and (r.Phase=="Shield"or r.Phase=="Active")then
  self:Finish(r)
 end
end
function Service:Finish(r)
 if not r or (r.Phase~="Shield"and r.Phase~="Active")then return false end
 local boss=self.Services.DestructionService:GetEntry(r.BossUid)
 if boss and boss.Alive and boss.Health>0 then return false end
 r.Phase="Complete"r.ReadyAt=now()+Config.Cooldown r.AttackAt=0 r.AttackKind=""r.WindowEnds=0
 self:RemoveTargets(r)
 for userId,item in pairs(r.Contributors)do
  local p=Players:GetPlayerByUserId(userId)
  if p and self.Data:IsLoaded(p)and item.Actions>=Config.MinimumActions and now()-item.Last<=Config.ContributionLifetime and not r.Rewarded[userId]then
   r.Rewarded[userId]=true
   self.Services.EconomyService:GrantRewards(p,r.Def.Rewards,"Expedition",r.Def.BossName.." DEFEATED")
  end
 end
 self:Publish(r)return true
end
function Service:ResolveHazard(r)
 local c=Config.BossPosition(r.Def)
 for _,p in Players:GetPlayers()do
  local root=aliveRoot(p)
  if root and self:InWorld(p,r.Def.Id)then
   local offset=root.Position-c local distance=Vector2.new(offset.X,offset.Z).Magnitude
   local hit=false
   if r.AttackKind=="Disc"then hit=distance<29
   elseif r.AttackKind=="Lane"then hit=distance<90 and math.abs(r.AttackAxis==0 and offset.X or offset.Z)<9
   elseif r.AttackKind=="Ring"then hit=distance>22 and distance<57 end
   if hit and root.Position.Y<7 then
    local h=p.Character:FindFirstChildOfClass("Humanoid")
    if h then h:TakeDamage(r.Enraged and 20 or 15)end
   end
  end
 end
 r.AttackAt=0 r.AttackKind=""r.NextAttack=now()+(r.Enraged and 4 or 7)
 self:Publish(r)
end
function Service:Tick(r)
 local stamp=now()
 if r.Phase=="Complete"then if stamp>=r.ReadyAt then r.Phase="Ready"self:Publish(r)end return end
 if r.Phase~="Shield"and r.Phase~="Active"then return end
 local boss=r.BossUid and self.Services.DestructionService:GetEntry(r.BossUid)
 if not boss then self:RemoveTargets(r)r.Phase="Ready"r.AttackAt=0 r.AttackKind=""self:Publish(r)return end
 local occupied=false for _,p in Players:GetPlayers()do if self:InWorld(p,r.Def.Id)then occupied=true break end end
 if occupied then r.LastOccupied=stamp
 elseif stamp-r.LastOccupied>=Config.IdleTimeout then
  self:RemoveTargets(r)r.Phase="Ready"r.AttackAt=0 r.AttackKind=""self:Publish(r)return
 end
 if r.Phase=="Active"then
  if r.WindowEnds>0 and stamp>=r.WindowEnds then self:MakeNodes(r)return end
  if r.AttackAt>0 then if stamp>=r.AttackAt then self:ResolveHazard(r)end
  elseif stamp>=r.NextAttack and occupied then
   r.AttackKind=r.Def.Attack r.AttackAxis=(r.AttackAxis+1)%2 r.AttackAt=stamp+1.8 self:Publish(r)
  end
 end
end
function Service:Rally(player,id)
 local r=records[id]
 if not r or not self:InWorld(player,id)then return false end
 local stamp=now()if stamp-(rallyAt[player]or -100)<30 then return false end rallyAt[player]=stamp
 for _,p in Players:GetPlayers()do
  if p~=player and self.Data:IsLoaded(p)then
   Notifier.Send(p,{Kind="Info",Text="CO-OP RALLY · "..r.Def.Name,Subtext="Open WORLDS to join the expedition.",Icon=r.Def.Icon})
  end
 end
 Notifier.Send(player,{Kind="Info",Text="RALLY SENT",Subtext="Players in this server can join through WORLDS."})
 return true
end
function Service:Init(services)
 self.Services=services self.Data=services.DataService
 local remote=RS.Remotes:FindFirstChild("ExpeditionAction")or Instance.new("RemoteEvent")remote.Name="ExpeditionAction"remote.Parent=RS.Remotes
 local states=RS:FindFirstChild("ExpeditionState")or Instance.new("Folder")states.Name="ExpeditionState"states.Parent=RS
 for _,def in Config.Worlds do
  local state=states:FindFirstChild(def.Id)or Instance.new("Folder")state.Name=def.Id state.Parent=states
  records[def.Id]={Def=def,State=state,Phase="Ready",Generation=0,NodesDone=0,Targets={},Contributors={},Rewarded={},Beacons={},ReadyAt=0,AttackAt=0,AttackAxis=0,WindowEnds=0}
 end
 services.DestructionService.Damaged:Connect(function(player,entry,amount)
  local id=uidWorld[entry.Uid]local r=id and records[id]
  if r and amount>0 then
   self:Contribute(player,r)
   if r.Def.Mechanic=="Beacons"and entry.Uid==r.BossUid and entry.Health<=entry.MaxHealth/2 then r.Enraged=true end
   self:Publish(r)
  end
 end)
 services.DestructionService.Wrecked:Connect(function(entry,credits)self:OnWreck(entry,credits)end)
end
function Service:Start()
 self.WorldFolder=Builder.Build()
 for _,r in pairs(records)do self:Publish(r)end
 for _,prompt in self.WorldFolder:GetDescendants()do
  if prompt:IsA("ProximityPrompt")and prompt:GetAttribute("ExpeditionAction")then
   if prompt:GetAttribute("ExpeditionAction")=="Beacon"then prompt.Enabled=false end
   prompt.Triggered:Connect(function(player)
    local root=aliveRoot(player)local parent=prompt.Parent
    if not root or not parent:IsA("BasePart")or (root.Position-parent.Position).Magnitude>17 then return end
    local id=prompt:GetAttribute("ExpeditionWorld")local action=prompt:GetAttribute("ExpeditionAction")
    if action=="Start"then self:StartEncounter(player,id)
    elseif action=="Return"then self.Services.ZoneService:Travel(player,"Plaza")
    elseif action=="Beacon"then self:ActivateBeacon(player,id,prompt:GetAttribute("BeaconIndex"))end
   end)
  end
 end
 self.Services.AntiExploitService:Connect("ExpeditionAction",{Rate=1,Burst=3},function(player,action,id)
  if type(action)~="string"or type(id)~="string"or not Config.ById[id]then return end
  if action=="Start"then self:StartEncounter(player,id)elseif action=="Rally"then self:Rally(player,id)end
 end)
 Players.PlayerRemoving:Connect(function(player)rallyAt[player]=nil end)
 task.spawn(function()
  local elapsed=0
  while true do task.wait(.15)elapsed+=.15
   for _,r in pairs(records)do self:Tick(r)if elapsed>=1 then self:Publish(r)end end
   if elapsed>=1 then elapsed=0 end
  end
 end)
end
return Service
