local Config=require(game.ReplicatedStorage.Shared.Config.ExpeditionConfig)
local CollectionService=game:GetService("CollectionService")
local Builder={}
local function model(parent,name)local m=Instance.new("Model")m.Name=name m.Parent=parent return m end
local function part(parent,name,size,cf,color,material,collide,shape)
 local p=Instance.new("Part")p.Name=name p.Size=size p.CFrame=cf p.Color=color
 p.Material=material or Enum.Material.SmoothPlastic p.Anchored=true
 p.CanCollide=collide==true p.CanTouch=false p.CanQuery=collide==true p.CastShadow=true
 if shape then p.Shape=shape end p.Parent=parent return p
end
local function motion(p,kind)p:SetAttribute("ExpeditionMotion",kind)CollectionService:AddTag(p,"ExpeditionAnimated")end
local function cylinder(parent,name,height,diameter,pos,color,material,collide)
 return part(parent,name,Vector3.new(height,diameter,diameter),CFrame.new(pos)*CFrame.Angles(0,0,math.pi/2),color,material,collide,Enum.PartType.Cylinder)
end
local function label(parent,name,text,size,pos,color,max)
 local l=Instance.new("TextLabel")l.Name=name l.Text=text l.Size=size l.Position=pos l.BackgroundTransparency=1 l.TextColor3=color l.TextScaled=true l.TextWrapped=true l.Font=Enum.Font.GothamBold l.Parent=parent
 local cap=Instance.new("UITextSizeConstraint")cap.MinTextSize=10 cap.MaxTextSize=max or 28 cap.Parent=l return l
end
local function sign(parent,pos,title,detail,color)
 local board=part(parent,"Board",Vector3.new(22,9,1),CFrame.new(pos),Color3.fromRGB(22,29,39),Enum.Material.Metal)
 local g=Instance.new("SurfaceGui")g.Name="Display"g.Face=Enum.NormalId.Front g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.PixelsPerStud=30 g.LightInfluence=0 g.MaxDistance=150 g.Parent=board
 label(g,"Heading",title,UDim2.new(1,-24,0,68),UDim2.fromOffset(12,10),color,38)
 label(g,"Detail",detail,UDim2.new(1,-24,1,-96),UDim2.fromOffset(12,82),Color3.fromRGB(223,231,240),25)
 return board
end
local function prompt(parent,action,world,text,object)
 local p=Instance.new("ProximityPrompt")p.Name=action p.ActionText=text p.ObjectText=object or text p.HoldDuration=action=="Beacon"and 1.2 or 0 p.MaxActivationDistance=13 p.RequiresLineOfSight=false
 p:SetAttribute("ExpeditionAction",action)p:SetAttribute("ExpeditionWorld",world)p.Parent=parent return p
end
local function ring(parent,pos,radius,color,count)
 count=count or 24
 for i=1,count do local a=i/count*math.pi*2 local v=pos+Vector3.new(math.cos(a)*radius,0,math.sin(a)*radius)
  part(parent,"Inlay",Vector3.new(2*math.pi*radius/count+.2,.15,1),CFrame.lookAt(v,pos),color,Enum.Material.Metal)
 end
end
function Builder.Templates()
 local folder=game.ServerStorage.Destructibles.Event
 for _,world in Config.Worlds do
  if not folder:FindFirstChild(world.Boss)then
   local boss=model(folder,world.Boss)
   local hit=part(boss,"Hitbox",Vector3.new(24,24,24),CFrame.new(0,12,0),world.Ground,nil,false)
   hit.Transparency=1 hit.CanQuery=true boss.PrimaryPart=hit
   local body=model(boss,"Visual")
   cylinder(body,"Waist",6,17,Vector3.new(0,9,0),world.Ground,Enum.Material.Metal)
   local torso=part(body,"Chest",Vector3.new(19,12,13),CFrame.new(0,16,0),world.Ground,Enum.Material.Metal)
   local core=part(body,"Core",Vector3.new(6,6,2),CFrame.new(0,17,-7),world.Color,Enum.Material.Neon,false,Enum.PartType.Ball)motion(core,"Core")
   part(body,"Visor",Vector3.new(14,5,10),CFrame.new(0,25,0),Color3.fromRGB(31,39,47),Enum.Material.Metal)
   for _,side in {-1,1}do
    part(body,"Eye",Vector3.new(3,1.1,.4),CFrame.new(side*3.5,25,-5.3),world.Accent,Enum.Material.Neon)
    part(body,"Leg",Vector3.new(6,9,7),CFrame.new(side*6,5,0),world.Ground,Enum.Material.Metal)
    part(body,"Foot",Vector3.new(9,3,12),CFrame.new(side*6,1.5,-3),Color3.fromRGB(41,49,57),Enum.Material.Metal)
    local arm=part(body,"Arm",Vector3.new(7,13,8),CFrame.new(side*15,16,0)*CFrame.Angles(0,0,side*.2),world.Ground,Enum.Material.Metal)motion(arm,"Arm")
    if world.Mechanic=="Roots"then
     for j=1,3 do
      local branch=part(body,"Antler",Vector3.new(2,7,2),CFrame.new(side*(7+j*2),27+j*3,1)*CFrame.Angles(0,0,-side*.5),Color3.fromRGB(115,133,91),Enum.Material.Wood)
      local leaf=part(body,"Leaf",Vector3.new(6,4,5),branch.CFrame*CFrame.new(0,4,0),world.Color,Enum.Material.Grass,false,Enum.PartType.Ball)motion(leaf,"Leaf")
     end
    elseif world.Mechanic=="Coolant"then
     for j=1,3 do
      local leg=part(body,"CrabLeg",Vector3.new(15,3,4),CFrame.new(side*20,5,j*6-12)*CFrame.Angles(0,side*.3,side*.15),world.Accent,Enum.Material.Metal)motion(leg,"Arm")
     end
     part(body,"Claw",Vector3.new(10,8,10),CFrame.new(side*23,13,-9),world.Color,Enum.Material.Metal)
    else
     for j=1,4 do
      local wing=part(body,"Wing",Vector3.new(5,15-j*2,2),CFrame.new(side*(12+j*5),22-j*2,3)*CFrame.Angles(0,0,-side*.28),j%2==0 and world.Accent or world.Ground,Enum.Material.Marble)motion(wing,"Wing")
     end
    end
   end
   if world.Mechanic=="Coolant"then part(body,"IceShell",Vector3.new(24,9,18),CFrame.new(0,22,6),world.Color,Enum.Material.Ice)end
   if world.Mechanic=="Beacons"then
    for j=1,12 do local a=j/12*math.pi*2 part(body,"Halo",Vector3.new(3,.6,1),CFrame.new(math.cos(a)*9,32,math.sin(a)*9)*CFrame.Angles(0,-a,0),world.Accent,Enum.Material.Metal)end
   end
  end
 end
 for _,id in {"PowerRoot","CoolantPipe"}do
  if not folder:FindFirstChild(id)then
   local def=Config.Objects[id]local m=model(folder,id)
   local root=cylinder(m,"Base",2,9,Vector3.new(0,1,0),def.Primary,Enum.Material.Metal,true)root.PivotOffset=CFrame.Angles(0,0,-math.pi/2)m.PrimaryPart=root
   cylinder(m,"Column",8,5,Vector3.new(0,5,0),def.Primary,id=="PowerRoot"and Enum.Material.Wood or Enum.Material.Metal)
   for j=1,3 do cylinder(m,"Band",.55,6.5,Vector3.new(0,j*2.3,0),def.Secondary,Enum.Material.Neon)end
   local orb=part(m,"Charge",Vector3.new(5,5,5),CFrame.new(0,10,0),def.Secondary,Enum.Material.Glass,false,Enum.PartType.Ball)motion(orb,"Orb")
  end
 end
end
local function vegetation(parent,center,world,rng)
 for i=1,20 do
  local a=i/20*math.pi*2 local radius=rng:NextNumber(98,146)local pos=center+Vector3.new(math.cos(a)*radius,0,math.sin(a)*radius)
  if pos.Z-center.Z>115 and math.abs(pos.X-center.X)<40 then continue end
  if world.Mechanic=="Roots"then
   local h=rng:NextNumber(13,24)cylinder(parent,"Trunk",h,3,pos+Vector3.new(0,h/2,0),Color3.fromRGB(85,74,61),Enum.Material.Wood)
   for j=1,3 do local leaf=part(parent,"Canopy",Vector3.new(17-j*2,9,16-j*2),CFrame.new(pos+Vector3.new(j%2*3,h+j*3,0)),Color3.fromRGB(52+j*9,98+j*10,70+j*5),Enum.Material.Grass,false,Enum.PartType.Ball)if j==3 then motion(leaf,"Leaf")end end
  elseif world.Mechanic=="Coolant"then
   local wedge=Instance.new("WedgePart")wedge.Name="IceCliff"wedge.Size=Vector3.new(rng:NextNumber(12,22),rng:NextNumber(12,34),18)wedge.CFrame=CFrame.new(pos+Vector3.new(0,wedge.Size.Y/2,0))*CFrame.Angles(0,-a,0)wedge.Color=world.Color wedge.Material=Enum.Material.Ice wedge.Anchored=true wedge.CanCollide=false wedge.CanQuery=false wedge.CanTouch=false wedge.Parent=parent
  else
   local h=rng:NextNumber(14,28)cylinder(parent,"BrokenPillar",h,5,pos+Vector3.new(0,h/2,0),Color3.fromRGB(131,129,151),Enum.Material.Marble)
   part(parent,"Capital",Vector3.new(8,3,8),CFrame.new(pos+Vector3.new(0,h,0)),world.Accent,Enum.Material.Marble)
   if i%3==0 then local stone=part(parent,"FloatingStone",Vector3.new(8,6,8),CFrame.new(pos+Vector3.new(0,h+9,0))*CFrame.Angles(.3,a,.2),world.Ground,Enum.Material.Slate)motion(stone,"Orb")end
  end
 end
end
local function landmark(parent,center,world)
 if world.Mechanic=="Roots"then
  local mill=model(parent,"ReclaimedFoundry")
  for _,x in {-105,105}do
   part(mill,"Factory",Vector3.new(31,22,45),CFrame.new(center+Vector3.new(x,11,-55)),Color3.fromRGB(66,78,73),Enum.Material.CorrodedMetal)
   for j=1,3 do part(mill,"Window",Vector3.new(1,7,7),CFrame.new(center+Vector3.new(x-math.sign(x)*16,14,-75+j*10)),world.Accent,Enum.Material.Glass)end
   cylinder(mill,"Chimney",46,8,center+Vector3.new(x,23,-74),Color3.fromRGB(83,80,72),Enum.Material.Brick)
   local rotor=part(mill,"WindRotor",Vector3.new(29,2,3),CFrame.new(center+Vector3.new(x,41,-50)),world.Accent,Enum.Material.Metal)motion(rotor,"Rotor")
  end
 elseif world.Mechanic=="Coolant"then
  local ship=model(parent,"Icebreaker")
  part(ship,"Hull",Vector3.new(33,14,86),CFrame.new(center+Vector3.new(-110,8,-35)),Color3.fromRGB(44,69,91),Enum.Material.Metal)
  part(ship,"Deck",Vector3.new(30,3,80),CFrame.new(center+Vector3.new(-110,16,-35)),world.Accent,Enum.Material.WoodPlanks)
  part(ship,"Bridge",Vector3.new(23,17,26),CFrame.new(center+Vector3.new(-110,26,-43)),Color3.fromRGB(175,191,199),Enum.Material.Metal)
  part(ship,"BridgeWindow",Vector3.new(.5,6,19),CFrame.new(center+Vector3.new(-98,27,-43)),world.Color,Enum.Material.Glass)
  for i=1,4 do part(parent,"Dock",Vector3.new(30,2,16),CFrame.new(center+Vector3.new(108,2,i*22-60)),Color3.fromRGB(81,98,112),Enum.Material.WoodPlanks,true)end
 else
  for _,x in {-100,100}do
   for _,z in {-70,-10}do part(parent,"TemplePier",Vector3.new(9,39,9),CFrame.new(center+Vector3.new(x,19.5,z)),Color3.fromRGB(123,121,145),Enum.Material.Marble)end
   part(parent,"TempleLintel",Vector3.new(14,7,72),CFrame.new(center+Vector3.new(x,40,-40)),world.Accent,Enum.Material.Marble)
  end
  for i=1,10 do local a=i*math.pi/5 local pos=center+Vector3.new(math.cos(a)*170,-25-i%3*8,math.sin(a)*170)
   part(parent,"SuspendedIsland",Vector3.new(20,14,27),CFrame.new(pos)*CFrame.Angles(.1,a,.2),world.Ground,Enum.Material.Slate)
  end
 end
end

function Builder.Dress(folder)
 for index,w in Config.Worlds do
  local world=folder:FindFirstChild(w.Id)
  if not world or world:FindFirstChild("ScenicDetails")then continue end
  local m=model(world,"ScenicDetails")local c=Config.Center(w)
  local rng=Random.new(991+index)
  -- Keep the arena and entry route clear; scenery sits outside the combat circle.
  for i=1,16 do
   local a=i/16*math.pi*2
   local pos=c+Vector3.new(math.cos(a)*151,0,math.sin(a)*151)
   local h=rng:NextNumber(16,36)
   part(m,"IslandCliff",Vector3.new(37,h,32),CFrame.new(pos+Vector3.new(0,-h*.5-3,0))*CFrame.Angles(0,a,.1),w.Ground,Enum.Material.Rock)
   if not(pos.Z-c.Z>110 and math.abs(pos.X-c.X)<55)then
    local rock=part(m,"Outcrop",Vector3.new(14,rng:NextNumber(5,12),10),CFrame.new(pos+Vector3.new(0,2,0))*CFrame.Angles(.15,a,.15),w.Ground:Lerp(w.Color,.22),w.Mechanic=="Coolant"and Enum.Material.Glacier or Enum.Material.Rock)
    if w.Mechanic=="Roots"then
     part(m,"Moss",Vector3.new(15,1.8,11),rock.CFrame*CFrame.new(0,rock.Size.Y/2,0),Color3.fromRGB(69,112,64),Enum.Material.Grass,false,Enum.PartType.Ball)
    end
   end
  end
  for _,side in {-1,1}do
   for j=1,5 do
    local pos=c+Vector3.new(side*17,0,50+j*17)
    cylinder(m,"PathPost",3,1.3,pos+Vector3.new(0,1.5,0),w.Ground,Enum.Material.Metal)
    cylinder(m,"PathCap",.5,2,pos+Vector3.new(0,3,0),w.Accent,Enum.Material.Glass)
   end
   part(m,"EntryPier",Vector3.new(4,19,5),CFrame.new(c+Vector3.new(side*17,9.5,140)),w.Ground:Lerp(w.Accent,.25),Enum.Material.Metal)
   for j=1,4 do
    local pos=c+Vector3.new(side*(75+j*12),.4,105-j*7)
    if w.Mechanic=="Roots"then
     for t=1,3 do part(m,"Fern",Vector3.new(2,5,7),CFrame.new(pos+Vector3.new(0,2,0))*CFrame.Angles(.3,t*2.1,side*.25),Color3.fromRGB(65,112,69),Enum.Material.Grass)end
    elseif w.Mechanic=="Coolant"then
     part(m,"SnowDrift",Vector3.new(20,3,12),CFrame.new(pos),Color3.fromRGB(193,218,225),Enum.Material.Snow,false,Enum.PartType.Ball)
    else
     part(m,"FallenMasonry",Vector3.new(10,4,5),CFrame.new(pos+Vector3.new(0,1,0))*CFrame.Angles(0,j*.5,.12),Color3.fromRGB(142,138,154),Enum.Material.Marble)
     part(m,"Rune",Vector3.new(4,.15,1),CFrame.new(pos+Vector3.new(0,3.2,0))*CFrame.Angles(0,j*.5,0),w.Accent,Enum.Material.Metal)
    end
   end
  end
  part(m,"EntryArch",Vector3.new(38,3,6),CFrame.new(c+Vector3.new(0,20,140)),w.Accent,Enum.Material.Metal)
  if w.Mechanic=="Roots"then
   for _,x in {-105,105}do
    part(m,"SawRoof",Vector3.new(35,3,49),CFrame.new(c+Vector3.new(x,23,-55)),Color3.fromRGB(47,66,59),Enum.Material.Metal)
    for j=1,4 do
     local pos=c+Vector3.new(x-math.sign(x)*16,16,-76+j*8)
     part(m,"WallVine",Vector3.new(1.3,17-j,2),CFrame.new(pos),Color3.fromRGB(63,110,72),Enum.Material.Grass)
    end
    cylinder(m,"Reservoir",13,16,c+Vector3.new(x,6.5,-14),Color3.fromRGB(91,97,77),Enum.Material.CorrodedMetal)
    for j=1,2 do cylinder(m,"ReservoirBand",1,17,c+Vector3.new(x,3+j*4,-14),w.Accent,Enum.Material.Metal)end
   end
  elseif w.Mechanic=="Coolant"then
   for i=1,3 do
    part(m,"FreightContainer",Vector3.new(17,12,28),CFrame.new(c+Vector3.new(116,6,-80+i*34)),i%2==0 and w.Accent or Color3.fromRGB(66,114,145),Enum.Material.Metal)
    for j=1,4 do part(m,"ContainerRib",Vector3.new(.7,11,.7),CFrame.new(c+Vector3.new(107,6,-94+i*34+j*5)),Color3.fromRGB(114,139,151),Enum.Material.Metal)end
   end
   part(m,"CraneTower",Vector3.new(5,46,5),CFrame.new(c+Vector3.new(132,23,-91)),w.Accent,Enum.Material.Metal)
   part(m,"CraneArm",Vector3.new(39,4,5),CFrame.new(c+Vector3.new(115,46,-91)),w.Accent,Enum.Material.Metal)
   part(m,"CraneCable",Vector3.new(.5,24,.5),CFrame.new(c+Vector3.new(97,33,-91)),Color3.fromRGB(60,68,76),Enum.Material.Metal)
   for j=1,5 do part(m,"Porthole",Vector3.new(.3,3,3),CFrame.new(c+Vector3.new(-93,10,-68+j*12)),w.Color,Enum.Material.Glass,false,Enum.PartType.Ball)end
  else
   for _,x in {-100,100}do
    part(m,"TempleFrieze",Vector3.new(15,1,73),CFrame.new(c+Vector3.new(x,42,-40)),w.Color,Enum.Material.Metal)
    for j=1,5 do
     part(m,"TempleStep",Vector3.new(21+j*3,.5,5),CFrame.new(c+Vector3.new(x,.5,14+j*5)),w.Ground:Lerp(w.Accent,.2),Enum.Material.Marble)
    end
   end
   for i=1,5 do
    local p=part(m,"SkyShard",Vector3.new(5,13,5),CFrame.new(c+Vector3.new((i-3)*22,32+i%2*8,-145))*CFrame.Angles(.3,i,.2),w.Color,Enum.Material.Glass)
    motion(p,"Orb")
   end
  end
 end
end

function Builder.Build()
 Builder.Templates()
 local map=workspace:WaitForChild("Map")
 if map:FindFirstChild("ExpeditionWorlds")then Builder.Dress(map.ExpeditionWorlds)return map.ExpeditionWorlds end
 local folder=Instance.new("Folder")folder.Name="ExpeditionWorlds"folder.Parent=map
 for index,world in Config.Worlds do
  local m=model(folder,world.Id)local c=Config.Center(world)local rng=Random.new(710+index)
  part(m,"Island",Vector3.new(320,10,320),CFrame.new(c+Vector3.new(0,-5,0)),world.Ground,world.Mechanic=="Coolant"and Enum.Material.Snow or Enum.Material.Slate,true)
  local arena=c+Vector3.new(0,0,-30)
  cylinder(m,"Arena",.4,166,arena+Vector3.new(0,.2,0),world.Ground:Lerp(Color3.new(0,0,0),.16),Enum.Material.Pavement,true)
  ring(m,arena+Vector3.new(0,.5,0),79,world.Color)
  for j=1,9 do part(m,"Path",Vector3.new(12,.3,10),CFrame.new(c+Vector3.new(0,.3,45+j*10)),world.Ground:Lerp(Color3.new(1,1,1),.2),Enum.Material.Cobblestone,true)end
  vegetation(m,c,world,rng)landmark(m,c,world)
  local board=sign(m,c+Vector3.new(25,9,127),world.Name,"FREE CO-OP EXPEDITION\nExplore, rally friends and launch a boss.\nAll tools can contribute.",world.Color)
  board.CFrame*=CFrame.Angles(0,math.pi,0)
  prompt(board,"Start",world.Id,"Launch encounter",world.BossName)
  local returnConsole=part(m,"ReturnConsole",Vector3.new(8,5,6),CFrame.new(c+Vector3.new(-20,2.5,137)),world.Accent,Enum.Material.Metal)
  prompt(returnConsole,"Return",world.Id,"Return to city","CITY PORTAL")
  local status=sign(m,c+Vector3.new(0,16,-118),world.BossName,"READY FOR YOUR TEAM\nStart from the entry console or WORLDS.",world.Color)
  status.Name="EncounterBoard"status.CFrame*=CFrame.Angles(0,math.pi,0)
  local beacons=Instance.new("Folder")beacons.Name="Beacons"beacons.Parent=m
  for i=1,world.Nodes do
   local pos=Config.NodePosition(world,i)
   local base=cylinder(beacons,"Beacon"..i,2,11,Vector3.new(pos.X,1,pos.Z),world.Ground,Enum.Material.Metal,true)
   base:SetAttribute("BeaconIndex",i)
   local orb=part(beacons,"BeaconOrb"..i,Vector3.new(4,4,4),CFrame.new(pos+Vector3.new(0,1,0)),world.Color,Enum.Material.Glass,false,Enum.PartType.Ball)
   orb:SetAttribute("BeaconIndex",i)motion(orb,"Orb")
   if world.Mechanic=="Beacons"then local p=prompt(base,"Beacon",world.Id,"Charge beacon","CO-OP BEACON")p:SetAttribute("BeaconIndex",i)end
  end
  local props=Instance.new("Folder")props.Name=world.Id props.Parent=workspace.Destructibles
  local names={"ScrapBarrel","WoodenCrate","TireStack","RoadSign"}
  for i=1,20 do
   local a=i/20*math.pi*2 local pos=c+Vector3.new(math.cos(a)*104,0,math.sin(a)*104)
   if pos.Z-c.Z>82 and math.abs(pos.X-c.X)<40 then continue end
   local source=game.ServerStorage.Destructibles.ScrapYard:FindFirstChild(names[(i-1)%#names+1])
   if source then
    local object=source:Clone()object:SetAttribute("Uid",nil)object:SetAttribute("Zone",world.Id)
    local box,size=object:GetBoundingBox()object:PivotTo(CFrame.new(pos+Vector3.new(0,size.Y/2+.5,0))*box:ToObjectSpace(object:GetPivot()))object.Parent=props
   end
  end
 end
 local gate=model(folder,"WorldsGate")
 local c=Vector3.new(0,0,112)
 for _,x in {-13,13}do part(gate,"Pillar",Vector3.new(4,24,5),CFrame.new(c+Vector3.new(x,12,0)),Color3.fromRGB(47,56,69),Enum.Material.Metal)end
 local b=sign(gate,c+Vector3.new(0,25,0),"WORLDS","THREE CO-OP EXPEDITIONS\nExplore · face bosses · rally friends",Color3.fromRGB(140,206,216))
 b.Size=Vector3.new(30,9,1)
 local console=part(gate,"Console",Vector3.new(5,4,5),CFrame.new(c+Vector3.new(10,2,-5)),Color3.fromRGB(78,126,144),Enum.Material.Metal)
 local p=Instance.new("ProximityPrompt")p.ActionText="Open WORLDS"p.ObjectText="CO-OP EXPEDITIONS"p.RequiresLineOfSight=false p.MaxActivationDistance=14 p:SetAttribute("Panel","Expeditions")p.Parent=console
 for i,w in Config.Worlds do local orb=part(gate,"WorldOrb",Vector3.new(4,4,4),CFrame.new(c+Vector3.new((i-2)*8,17,0)),w.Color,Enum.Material.Glass,false,Enum.PartType.Ball)motion(orb,"Orb")end
 Builder.Dress(folder)
 return folder
end
return Builder
